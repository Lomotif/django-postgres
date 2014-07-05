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
    r'^\W*(?P<lower_bound>[\[\(])'
    r'(?P<lower>.+)?'
    r','
    r'(?P<upper>.+)?'
    r'(?P<upper_bound>[\]\)])\W*$'
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

    data['lower'] = cast(data['lower'])
    data['upper'] = cast(data['upper'])

    return cls(**data)


def is_range(value):
    if isinstance(value, six.string_types):
        return RANGE_RE.match(value)

    if isinstance(value, Range):
        return True

    # Does it quack like a range?
    return all([hasattr(value, x) for x in ['upper', 'lower', 'upper_inc', 'lower_inc']])


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


class Int8RangeField(NumericRangeField):
    def db_type(self, connection):
        return 'int8range'

    def get_internal_type(self):
        return 'Int8RangeField'



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



class RangeLookup(models.Lookup):
    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs
        # We need to cast a string that looks like a range
        # to a range of the correct type, so psycopg2 will
        # adapt it correctly.
        if isinstance(rhs, six.string_types) and RANGE_RE.match(rhs):
            self.rhs = range_from_string(self.lhs.source.range_type, rhs)

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = '%s', [self.rhs]
        params = lhs_params + rhs_params
        return '%s %s %s' % (lhs, self.operator, rhs), params


@RangeField.register_lookup
class RangeOverlapsLookup(RangeLookup):
    lookup_name = 'overlaps'
    operator = '&&'


@RangeField.register_lookup
class RangeContainsLookup(RangeLookup):
    lookup_name = 'contains'
    operator = '@>'


@RangeField.register_lookup
class RangeInLookup(RangeLookup):
    lookup_name = 'in'
    operator = '<@'


@RangeField.register_lookup
class RangeLeftOfLookup(RangeLookup):
    lookup_name = 'left_of'
    operator = '<<'


@RangeField.register_lookup
class RangeRightOfLookup(RangeLookup):
    lookup_name = 'right_of'
    operator = '>>'


@RangeField.register_lookup
class RangeNotExtendsRightOfLookup(RangeLookup):
    lookup_name = 'not_extends_right_of'
    operator = '&<'


@RangeField.register_lookup
class RangeNotExtendsLeftOfLookup(RangeLookup):
    lookup_name = 'not_extends_left_of'
    operator = '&>'


@RangeField.register_lookup
class RangeAdjacentTo(RangeLookup):
    lookup_name = 'adjacent_to'
    operator = '-|-'


def InRangeFactory(RangeType, range_cast=None, column_cast=None):
    if not range_cast:
        range_cast = RangeType.__name__.lower()
    if not column_cast:
        column_cast = RangeType.__name__.lower().replace('range', '')

    class InRange(models.lookups.BuiltinLookup):
        lookup_name = 'in'

        def __init__(self, lhs, rhs):
            self.lhs, self.rhs = lhs, rhs
            if not is_range(self.rhs):
                self.rhs = self.get_prep_lookup()

        def as_sql(self, qn, connection):
            if is_range(self.rhs):
                return self.in_range_sql(qn, connection)

            return super(InRange, self).as_sql(qn, connection)


        def in_range_sql(self, qn, connection):
            lhs, lhs_params = self.process_lhs(qn, connection)
            rhs, rhs_params = '%s', [self.rhs]
            params = lhs_params + rhs_params

            return '%s::%s <@ %s::%s' % (
                lhs, column_cast,
                rhs, range_cast
            ), params

    return InRange

models.DateField.register_lookup(InRangeFactory(DateRange))
models.IntegerField.register_lookup(InRangeFactory(NumericRange, range_cast='int4range', column_cast='integer'))
