import re
from decimal import Decimal

from django.db import models
from django.utils import six

from psycopg2._range import Range, DateRange, DateTimeRange, NumericRange

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

RANGE_RE = re.compile(
    r'^(?P<lower_bound>[\[\(])'
    r'(?P<lower>.+)?'
    r',\W*'
    r'(?P<upper>.+)?'
    r'(?P<upper_bound>[\]\)])$'
)

NUMBER_RE = re.compile(
    r'^\d*\.?\d*$'
)
DATE_RE = re.compile(
    r'^(?P<year>\d\d\d\d)-(?P<month>(0\d)|(1[012]))-(?P<day>([012]\d)|(3[01]))$'
)

def cast(value):
    if not value:
        return None

    if NUMBER_RE.match(value):
        if '.' in value:
            return Decimal(value)
        return int(value)

    if DATE_RE.match(value):
        return datetime.date(**dict(
            (key,int(value)) for key,value in DATE_RE.match(value).groupdict()
        ))

    return None

def range_from_string(cls, value):
    match = RANGE_RE.match(value)
    if not match:
        raise forms.ValidationError(_('Invalid range string'))

    data = match.groupdict()
    data['bounds'] = '%s%s' % (
        data.pop('lower_bound'), data.pop('upper_bound')
    )

    data['lower'] = cast(value)
    data['upper'] = cast(value)

    return cls(**value)


class RangeField(models.Field):
    range_type= Range

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self.formfield_class,
            'range_type': self.range_type
        }
        defaults.update(kwargs)
        return super(RangeField, self).formfield(**defaults)


class NumericRangeField(RangeField):
    range_type = NumericRange
    formfield_class = range_fields.NumericRangeField

class Int4RangeField(NumericRangeField):

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


class DateTimeRangeField(RangeField):
    range_type = DateTimeRange
    formfield_class = range_fields.DateTimeRangeField


class RangeOverlapsLookup(models.Lookup):
    lookup_name = 'overlaps'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s && %s' % (lhs, rhs), params

RangeField.register_lookup(RangeOverlapsLookup)


def InRangeFactory(RangeType, range_cast=None, column_cast=None):
    if not range_cast:
        range_cast = RangeType.__name__.lower()
    if not column_cast:
        column_cast = RangeType.__name__.lower().replace('range', '')



    class InRange(models.Lookup):
        lookup_name = 'in'

        def __init__(self, lhs, rhs):
            self.lhs, self.rhs = lhs, rhs
            if not isinstance(self.rhs, RangeType) and not RANGE_RE.match(self.rhs):
                self.rhs = self.get_prep_lookup()

        def as_sql(self, qn, connection):
            if isinstance(self.rhs, six.string_types):
                if RANGE_RE.match(self.rhs):
                    return self.in_range_sql(qn, connection)

            if isinstance(self.rhs, RangeType):
                return self.in_range_sql(qn, connection)

            return super(InRange, self).as_sql(qn, connection)


        def in_range_sql(self, qn, connection):
            lhs, lhs_params = self.process_lhs(qn, connection)
            rhs, rhs_params = '%s', [unicode(self.rhs)]
            params = lhs_params + rhs_params

            return '%s::%s <@ %s::%s' % (
                lhs, column_cast,
                rhs, range_cast
            ), params

    return InRange

models.DateField.register_lookup(InRangeFactory(DateRange))
models.IntegerField.register_lookup(InRangeFactory(NumericRange, range_cast='int4range', column_cast='integer'))