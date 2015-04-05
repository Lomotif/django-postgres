from django.db.models import fields
from django.db import connection
from django.dispatch import receiver, Signal

from psycopg2.extras import register_composite
from psycopg2.extensions import register_adapter, adapt, AsIs
from psycopg2 import ProgrammingError


class CompositeBase(type):
    """
    Metaclass for all Composite Types.

    At this stage, no inheritance is available for
    CompositeField types.
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(CompositeBase, cls).__new__

        # Ensure initialization is only performed for subclasses,
        # not the CompositeType class itself.
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        # Don't need abstract, etc, but we do need a ._meta to enable
        # adding fields to us.
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        app_label = None
        app_config = apps.get_containing_app_config(module)

        if getattr(meta, 'app_label', None) is None:
            if app_config is None:
                raise RuntimeError(
                    "CompositeField class %s.%s doesn't declare an explicit "
                    "app_label and either isn't in an application in "
                    "INSTALLED_APPS or else was imported before its "
                    "application was loaded. " % (module, name)
                )
            else:
                app_label = app_config.label

        new_class.add_to_class('_meta', Options(meta, app_label))

        # Add the attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        field_names = {f.name for f in new_class._meta.local_fields}

    def add_to_class(cls, name, value):
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class CompositeType(six.with_metaclass(CompositeBase)):
    def clean_fields(self, exclude=None):
        if exclude is None:
            exclude = []

        errors = {}
