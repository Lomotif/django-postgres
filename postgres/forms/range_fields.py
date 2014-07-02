
from django import forms

from psycopg2.extras import Range, NumericRange

LOWER = [('(', '('), ('[', '[')]
UPPER = [(')', ')'), (']', ']')]

class RangeWidget(forms.MultiWidget):
    def __init__(self):
        return super(RangeWidget, self).__init__(widgets=[
            forms.Select(choices=LOWER),
            forms.TextInput,
            forms.TextInput,
            forms.Select(choices=UPPER)
        ])

    def decompress(self, value):
        if not value:
            return ['(', None, None, ')']
        return [
            value._bounds[0],
            value.lower,
            value.upper,
            value._bounds[1]
        ]

class RangeField(forms.MultiValueField):
    widget = RangeWidget

    def __init__(self, *args, **kwargs):
        self.range_type = kwargs.pop('range_type', Range)

        fields = (
            forms.ChoiceField(choices=LOWER),
            forms.IntegerField(),
            forms.IntegerField(),
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
