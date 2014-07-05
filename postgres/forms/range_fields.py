
from django import forms

from psycopg2.extras import Range, NumericRange, DateRange, DateTimeRange

LOWER = [('(', '('), ('[', '[')]
UPPER = [(')', ')'), (']', ']')]

class RangeWidget(forms.MultiWidget):
    base_widget = None

    def __init__(self):
        return super(RangeWidget, self).__init__(widgets=[
            forms.Select(choices=LOWER),
            self.base_widget,
            self.base_widget,
            forms.Select(choices=UPPER)
        ])

    def decompress(self, value):
        if not value:
            return None
        return [
            value._bounds[0],
            value.lower,
            value.upper,
            value._bounds[1]
        ]


class DateRangeWidget(RangeWidget):
    base_widget = forms.DateInput

class NumericRangeWidget(RangeWidget):
    base_widget = forms.TextInput


class RangeField(forms.MultiValueField):
    widget = None
    base_field = None
    range_type = None

    def __init__(self, *args, **kwargs):
        self.range_type = kwargs.pop('range_type', Range)
        self.base_field = kwargs.pop('base_field', forms.IntegerField)
        self.widget = kwargs.pop('widget', self.widget)

        fields = (
            forms.ChoiceField(choices=LOWER),
            self.base_field(),
            self.base_field(),
            forms.ChoiceField(choices=UPPER)
        )

        return super(RangeField, self).__init__(
            fields=fields, *args, **kwargs
        )

    def clean(self,value):
        return self.compress([
            self.fields[i].clean(v) for i,v in enumerate(value)
        ])

    def compress(self, data_list):
        return self.range_type(
            lower=data_list[1],
            upper=data_list[2],
            bounds='%s%s' % (data_list[0], data_list[3])
        )



class DateRangeField(RangeField):
    widget = DateRangeWidget
    base_field = forms.DateField
    range_type = DateRange


class DateTimeRangeField(DateRangeField):
    range_type = DateTimeRange


class NumericRangeField(RangeField):
    widget = NumericRangeWidget
    base_field = forms.IntegerField
    range_type = NumericRange