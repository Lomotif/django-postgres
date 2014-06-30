from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from psycopg2.extras import DateRange

from .models import AuditLog


class AuditQueryForm(forms.Form):
    start = forms.DateField()
    finish = forms.DateField()

    def get_queryset(self):
        date_range = DateRange(
            lower=self.cleaned_data['start'],
            upper=self.cleaned_data['finish'],
            bounds='[)'
        )

        return AuditLog.objects.filter(timestamp__in=date_range)

    #
    # page = forms.IntegerField(required=False, initial=1)
    #
    # paginate_by = 25
    #
    # def __init__(self, *args, **kwargs):
    #     self.paginate_by = kwargs.pop('paginate_by', self.paginate_by)
    #     super(AuditQueryForm, self).__init__(*args, **kwargs)
    #     self.data = self.data.copy()
    #
    # def clean_page(self):
    #     return self.cleaned_data['page'] or 1
    #
    # def fetch_audit_logs(self):
    #     date_range = DateRange(
    #         lower=self.cleaned_data['start'],
    #         upper=self.cleaned_data['finish'],
    #         bounds='[)'
    #     )
    #
    #     return AuditLog.objects.filter(timestamp__in=date_range)
    #
    # def paginate_queryset(self, queryset):
    #     paginator = Paginator(queryset, 25)
    #     # Missing or 0 page number reverts to 1
    #     page_number = self.cleaned_data['page']
    #
    #     # Negative page number counts back from last page.
    #     if page_number < 0:
    #         page_number = paginator.num_pages + page_number + 1
    #
    #     # But we always normalise the page number.
    #     self.data['page'] = page_number
    #
    #     try:
    #         return paginator, paginator.page(page_number)
    #     except EmptyPage:
    #         return paginator, paginator.page(paginator.num_pages)
    #     except InvalidPage as e:
    #         import pdb; pdb.set_trace()
    #
    # def get_paginated_data(self):
    #     queryset = self.fetch_audit_logs()
    #     paginator, page = self.paginate_queryset(queryset)
    #     return {
    #         'paginator': paginator,
    #         'page_obj': page,
    #         'queryset': page.object_list,
    #         'is_paginated': page.has_other_pages(),
    #     }
