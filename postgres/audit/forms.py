import datetime

from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from .models import AuditLog


class AuditQueryForm(forms.Form):
    start = forms.DateField()
    finish = forms.DateField()

    def get_queryset(self):
        start = self.cleaned_data['start']
        finish = self.cleaned_data['finish'] + datetime.timedelta(1)

        return AuditLog.objects.filter(timestamp__range=(start, finish)).order_by('-timestamp')