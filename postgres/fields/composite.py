import inspect

from django import forms
from django.db import connection
from django.db.models import fields
from django.db.models.base import ModelBase
from django.dispatch import receiver, Signal
from django.utils import six
from django.utils.translation import ugettext as _

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

    def formfield(self, **kwargs):
        defaults = {
            'form_class': composite_formfield_factory(self.__class__)
        }
        defaults.update(**kwargs)
        return super(CompositeField, self).formfield(**defaults)


composite_type_created = Signal(providing_args=['name'])


@receiver(composite_type_created)
def register_composite_late(sender, db_type, **kwargs):
    _missing_types.pop(db_type).register_composite()


def composite_field_factory(name, db_type, **fields):
    fields['db_type'] = lambda self, connection: db_type
    fields['__module__'] = CompositeField.__module__
    return type(name, (CompositeField,), fields)


def composite_formfield_factory(CompositeField):
    fields = CompositeField._meta.fields

    class CompositeFormField(forms.MultiValueField):
        class widget(forms.MultiWidget):
            def __init__(self):
                return super(CompositeFormField.widget, self).__init__(widgets=[
                    field.formfield().widget for field in fields
                ])

        def __init__(self, *args, **kwargs):
            if 'fields' not in kwargs:
                kwargs['fields'] = [
                    field.formfield() for field in fields
                ]
            return super(CompositeFormField, self).__init__(*args, **kwargs)

        def clean(self, value):
            if not value:
                return None
            if isinstance(value, six.string_types):
                value = value.split(',')

            if len(fields) != len(value):
                raise forms.ValidationError('arity of data does not match {}'.format(CompositeField.__name__))

            cleaned_data = [field.clean(val) for field, val in zip(self.fields, value)]

            none_data = [x is None for x in cleaned_data]

            if any(none_data) and not all(none_data):
                raise forms.ValidationError(_('Either no values, or all values must be entered'))

            return CompositeField(
                **{field.name: val for field, val in zip(fields, cleaned_data)}
            )

    return CompositeFormField
