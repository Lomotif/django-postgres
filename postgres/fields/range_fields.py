from django.db import models
from django import forms
from django.utils import six

from psycopg2._range import Range

# Monkey patch Range so that we get a a string that can
# be used to save.
def range_to_string(value):
    if value and not isinstance(value, six.string_types):
        lower, upper = value._bounds
        return '%s%s,%s%s' % (
            lower, value.lower, value.upper, upper
        )
    return value

Range.__unicode__ = range_to_string

class RangeField(models.Field):
    pass


class Int4RangeField(RangeField):
    def db_type(self, connection):
        return 'int4range'

    def get_internal_type(self):
        return 'Int4RangeField'

