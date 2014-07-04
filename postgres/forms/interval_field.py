import datetime
import re

from django import forms

INTERVAL_RE = re.compile(
    r'^((?P<days>\d+) days)?,?\W*'
    r'((?P<hours>\d\d?)(:(?P<minutes>\d\d)(:(?P<seconds>\d\d))?)?)?'
)

def build_interval(data):
    match = INTERVAL_RE.match(data)
    if match:
        return datetime.timedelta(**dict(
            (key,int(value)) for key,value in match.groupdict().items() if value is not None
        ))

class IntervalField(forms.CharField):
    def clean(self, value):
        if value:
            if not INTERVAL_RE.match(value):
                raise forms.ValidationError('Does not match interval format.')
            return build_interval(value)