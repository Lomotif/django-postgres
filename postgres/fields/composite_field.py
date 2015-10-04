import inspect
import sys

from django import forms
from django.db import connection
from django.db.models import fields
from django.db.models.base import ModelBase
from django.utils import six
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from psycopg2.extras import register_composite, CompositeCaster
from psycopg2.extensions import register_adapter, adapt, AsIs
from psycopg2 import ProgrammingError, OperationalError

__all__ = ['CompositeType', 'composite_type_factory']

# When types don't yet exist in the database, we want to stash
# them here, so we can register them later (or throw exceptions
# if we attempt to create an object).
_missing_types = {}
# We also don't want to attempt to reregister.
_registered_types = {}


def adapt_composite(composite):
    value = ','.join([
        adapt(getattr(composite, field.attname)).getquoted().decode('utf-8')
        for field in composite._meta.fields
    ])
    return AsIs("({})::{}".format(value, composite.db_type))


class CompositeMeta(ModelBase):
    """
    A metaclass that uses some of the functionality that django Models
    use: adding a field to a CompositeType declaration must create a
    field on that object, similar to how model fields work.
    """
    def __new__(cls, name, bases, attrs):
        if 'Meta' not in attrs:
            attrs['Meta'] = type('Meta', (object,), {})

        # types are always abstract.
        attrs['Meta'].abstract = True

        new_class = super(CompositeMeta, cls).__new__(cls, name, bases, attrs)

        # We only want to register subclasses of CompositeField, not the
        # CompositeField class itself.
        parents = [b for b in bases if isinstance(b, CompositeMeta)]
        if parents:
            if new_class.db_type is None:
                raise ValueError('You must set a db_type for {}'.format(name))

            new_class.register_composite()

            fields = new_class._meta.fields
            form_fields = [f.formfield() for f in fields]
            widgets = [f.widget for f in form_fields]

            # We may as well create a FormField subclass, too.
            widget = type('{}Widget'.format(name), (forms.MultiWidget,), {
                '__init__': lambda self: forms.MultiWidget.__init__(self, widgets=widgets),
                'decompress': lambda self, value: value or new_class()
            })

            def clean(self, value):
                if not value:
                    return None
                if isinstance(value, six.string_types):
                    value = value.split(',')

                if len(fields) != len(value):
                    raise forms.ValidationError('arity of data does not match {}'.format(new_class.__name__))

                cleaned_data = [field.clean(val) for field, val in zip(self.fields, value)]

                none_data = [x is None for x in cleaned_data]

                if any(none_data) and not all(none_data):
                    raise forms.ValidationError(_('Either no values, or all values must be entered'))

                return new_class(*cleaned_data)

            form_field = type('{}FormField'.format(name), (forms.MultiValueField,), {
                '__init__': lambda self, *args, **kwargs: forms.MultiValueField.__init__(self, *args, fields=form_fields, **kwargs),
                'widget': widget,
                'clean': clean
            })
            # We also want to create a Field subclass, with the same name as
            # we have, but with Field appended. Perhaps we should be looking
            # for an existing Field subclass in this module before creating it?
            field = type('{}Field'.format(name), (BaseCompositeField,), {
                'db_type': lambda self, connection: new_class.db_type,
                'python_type': new_class,
                'formfield': lambda self, *args, **kwargs: form_field(*args, **kwargs)
            })

            # Add the field to the module our type was declared in.
            setattr(sys.modules[new_class.__module__], field.__name__, field)
            new_class._field = field

            setattr(sys.modules[new_class.__module__], widget.__name__, widget)
            setattr(sys.modules[new_class.__module__], form_field.__name__, form_field)

        return new_class

    def add_to_class(cls, name, value):
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def register_composite(cls):
        db_type = cls.db_type

        class Caster(CompositeCaster):
            def make(self, values):
                return cls(**dict(zip(self.attnames, values)))

        if db_type in _registered_types:
            raise ValueError('Type {} has already been registered.'.format(db_type))

        try:
            _registered_types[db_type] = register_composite(
                db_type,
                connection.cursor().cursor,
                globally=True,
                factory=Caster
            )
        except (ProgrammingError, OperationalError) as exc:
            _missing_types[db_type] = (cls, exc)
        else:
            register_adapter(cls, adapt_composite)
            _missing_types.pop(db_type, None)


class BaseCompositeField(fields.Field):
    def deconstruct(self):
        # We may have dynamically created this class, and stuck it in the relevant
        # module, so we need to ensure that the migrations framework will look there
        # for it.
        name, path, args, kwargs = super(BaseCompositeField, self).deconstruct()
        path = path.replace('postgres.fields.composite_field', self.python_type.__module__)
        return name, path, args, kwargs

    def get_default(self):
        # Are there "inner" defaults?
        return self.python_type()

    def to_python(self, value):
        if isinstance(value, self.python_type):
            return value

        if value is None:
            return value

        return self.python_type(value)


class CompositeType(six.with_metaclass(CompositeMeta)):
    db_type = None

    def __init__(self, *args, **kwargs):
        if self.db_type in _missing_types:
            self.__class__.register_composite()
            # If it's still not registered, re-raise the exception.
            # if self.db_type in _missing_types:
            #     raise _missing_types[self.db_type][1]

        # Now populate the inner values. This bit is stolen directly
        # from the django model __init__ method.
        # Firstly, deal with any *args passed to the method.
        fields_iter = iter(self._meta.fields)
        for val, field in zip(args, fields_iter):
            setattr(self, field.attname, val)
            kwargs.pop(field.name, None)

        # Now deal with any that are in kwargs.
        for field in fields_iter:
            if kwargs:
                try:
                    val = kwargs.pop(field.attname)
                except KeyError:
                    # See django issue #12057: don't eval get_default() unless necessary.
                    val = field.get_default()
            else:
                val = field.get_default()

            setattr(self, field.attname, val)

        super(CompositeType, self).__init__()

    __unicode__ = adapt_composite

    def __getitem__(self, i):
        return getattr(self, self._meta.fields[i].name)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        return force_text(dict(field.flatchoices).get(value, value), strings_only=True)


def composite_type_factory(name, db_type, **fields):
    frame = inspect.stack()[1][0]
    if '__name__' not in frame.f_locals:
        raise ValueError('You may only create classes at the module level.')

    module = sys.modules[frame.f_locals['__name__']]

    assert isinstance(db_type, six.string_types), 'db_type must be a string type, not {}'.format(type(db_type))

    fields['db_type'] = db_type
    fields['__module__'] = module.__name__

    new_class = type(name, (CompositeType,), fields)
    setattr(module, name, new_class)

    return new_class

# def composite_field_factory(name, db_type, **fields):
#     fields['db_type'] = lambda self, connection: db_type
#     fields['__module__'] = CompositeField.__module__
#     return type(name, (CompositeField,), fields)
#
#
# def composite_formfield_factory(CompositeField):
#     fields = CompositeField._meta.fields
#
#     class CompositeFormField(forms.MultiValueField):
#         class widget(forms.MultiWidget):
#             def __init__(self):
#                 return super(CompositeFormField.widget, self).__init__(widgets=[
#                     field.formfield().widget for field in fields
#                 ])
#
#         def __init__(self, *args, **kwargs):
#             if 'fields' not in kwargs:
#                 kwargs['fields'] = [
#                     field.formfield() for field in fields
#                 ]
#             return super(CompositeFormField, self).__init__(*args, **kwargs)
#
#         def clean(self, value):
#             if not value:
#                 return None
#             if isinstance(value, six.string_types):
#                 value = value.split(',')
#
#             if len(fields) != len(value):
#                 raise forms.ValidationError('arity of data does not match {}'.format(CompositeField.__name__))
#
#             cleaned_data = [field.clean(val) for field, val in zip(self.fields, value)]
#
#             none_data = [x is None for x in cleaned_data]
#
#             if any(none_data) and not all(none_data):
#                 raise forms.ValidationError(_('Either no values, or all values must be entered'))
#
#             return CompositeField(
#                 **{field.name: val for field, val in zip(fields, cleaned_data)}
#             )
#
#     return CompositeFormField
