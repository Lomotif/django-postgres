import inspect

from django.db.models import fields
from django.db.models.base import ModelBase
from django.db import connection
from django.dispatch import receiver, Signal
from django.utils import six

from psycopg2.extras import register_composite, CompositeCaster
from psycopg2.extensions import register_adapter, adapt, AsIs
from psycopg2 import ProgrammingError


_missing_types = {}


class CompositeMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        # Always abstract.
        if 'Meta' not in attrs:
            attrs['Meta'] = type('Meta', (object,), {})

        attrs['Meta'].abstract = True

        new_class = super(CompositeMeta, cls).__new__(cls, name, bases, attrs)

        # We only want to register subclasses of CompositeField, not the
        # CompositeField class itself.
        parents = [b for b in bases if isinstance(b, CompositeMeta)]
        if parents:
            new_class.register_composite()

        return new_class

    def add_to_class(cls, name, value):
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def register_composite(cls):
        class Caster(CompositeCaster):
            def make(self, values):
                return cls(**dict(zip(self.attnames, values)))

        db_type = cls().db_type(connection)
        if db_type:
            try:
                register_composite(
                    db_type,
                    connection.cursor().cursor,
                    globally=True,
                    factory=Caster
                )
            except ProgrammingError:
                _missing_types[db_type] = cls
            else:
                def adapt_composite(composite):
                    return AsIs("(%s)::%s" % (
                        ", ".join([
                            adapt(getattr(composite, field.attname)).getquoted()
                            for field in composite._meta.fields
                        ]), db_type
                    ))

                register_adapter(cls, adapt_composite)


class CompositeField(six.with_metaclass(CompositeMeta, fields.Field)):
    # We should also incorporate the stuff from SubFieldBase, so
    # we convert any iterable of the correct arity, and coercable types
    # into the python_type.
    """
    A handy base class for defining your own composite fields.

    It registers the composite type.
    """

    def __init__(self, *args, **kwargs):
        fields_iter = iter(self._meta.fields)
        for val, field in zip(args, fields_iter):
            setattr(self, field.attname, val)
            kwargs.pop(field.name, None)

        for field in fields_iter:
            if kwargs:
                try:
                    val = kwargs.pop(field.attname)
                except KeyError:
                    # See django issue #12057: don't eval get_default() unless
                    # necessary.
                    val = field.get_default()
            else:
                val = field.get_default()

            setattr(self, field.attname, val)

        super(CompositeField, self).__init__()

    def __unicode__(self):
        return '({fields})::{type}'.format(
            type=self.db_type(None),
            fields=', '.join([
                str(getattr(self, f.attname))
                for f in self._meta.fields
            ])
        )

    def db_type(self, connection):
        if hasattr(self, '_db_type'):
            return self._db_type

        raise NotImplemented('You must provide a db_type method.')


composite_type_created = Signal(providing_args=['name'])


@receiver(composite_type_created)
def register_composite_late(sender, db_type, **kwargs):
    _missing_types.pop(db_type).register_composite()
