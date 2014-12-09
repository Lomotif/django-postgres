from django.db import models


from ..forms.interval_field import IntervalField as IntervalFormField


class IntervalField(models.Field):
    description = 'Interval Field'

    def db_type(self, connection):
        return 'interval'

    def get_internal_type(self):
        return 'IntervalField'

    def get_prep_value(self, value):
        if value == '' and self.null:
            return None
        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': IntervalFormField}
        defaults.update(kwargs)
        return super(IntervalField, self).formfield(**defaults)