from __future__ import unicode_literals

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six

from psycopg2.extras import register_uuid

register_uuid()

class UUIDField(six.with_metaclass(models.SubfieldBase, models.Field)):
    """
    We can make use of psycopg2's uuid handling: that means everything
    at the database end will be a uuid.

    We also make sure that values assigned to this field on a model
    will automatically be cast to UUID.
    """
    description = "UUID"

    def __init__(self, *args, **kwargs):
        self.auto = kwargs.pop('auto', False)
        # Using this column as a primary_key implies auto.
        # Because we are a uuidfield, we can set ourself, and
        # not rely on the server.
        if kwargs.get('primary_key', False):
            self.auto = True
        super(UUIDField, self).__init__(*args, **kwargs)


    def get_default(self):
        if self.auto:
            return uuid.uuid4()

    def get_internal_type(self):
        return 'UUIDField'

    def db_type(self, connection):
        return 'uuid'

    def to_python(self, value):
        if isinstance(value, six.string_types):
            if not value:
                if self.null:
                    return None
                if self.blank:
                    return ''
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError as exc:
            raise ValidationError(*exc.args)


# Lookups for UUIDField.
# Which ones acutally make sense? Any that we need to handle custom?
