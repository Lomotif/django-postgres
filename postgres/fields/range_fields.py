from django.db import models
from django.utils import six

from psycopg2._range import Range, DateRange, NumericRange

from ..forms import range_fields

# Monkey patch Range so that we get a a string that can
# be used to save. This may go away when we have proper
# fields.
def range_to_string(value):
    if value and not isinstance(value, six.string_types):
        lower, upper = value._bounds
        return '%s%s,%s%s' % (
            lower, value.lower or '', value.upper or '', upper
        )
    return value

Range.__unicode__ = range_to_string


class RangeField(models.Field):
    range_type= Range

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self.formfield_class,
            'range_type': self.range_type
        }
        defaults.update(kwargs)
        return super(RangeField, self).formfield(**defaults)


class Int4RangeField(RangeField):
    range_type = NumericRange
    formfield_class = range_fields.NumericRangeField

    def db_type(self, connection):
        return 'int4range'

    def get_internal_type(self):
        return 'Int4RangeField'



class DateRangeField(RangeField):
    range_type = DateRange
    formfield_class = range_fields.DateRangeField

    def db_type(self, connection):
        return 'daterange'

    def get_internal_type(self):
        return 'DateRangeField'


class RangeOverlapsLookup(models.Lookup):
    lookup_name = 'overlaps'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s && %s' % (lhs, rhs), params

RangeField.register_lookup(RangeOverlapsLookup)


def InRangeFactory(RangeType):
    class InRange(models.Lookup):
        lookup_name = 'in'
        range_cast = RangeType.__name__.lower()
        column_cast = range_cast.replace('range', '')

        def __init__(self, lhs, rhs):
            self.lhs, self.rhs = lhs, rhs
            if not isinstance(self.rhs, RangeType):
                self.rhs = self.get_prep_lookup()

        def as_sql(self, qn, connection):
            if not isinstance(self.rhs, RangeType):
                return super(InRange, self).as_sql(qn, connection)

            lhs, lhs_params = self.process_lhs(qn, connection)
            rhs, rhs_params = '%s', [unicode(self.rhs)]
            params = lhs_params + rhs_params
            return '%s::%s <@ %s::%s' % (
                lhs, self.column_cast, rhs, self.range_cast
            ), params

    return InRange

models.DateField.register_lookup(InRangeFactory(DateRange))