import json
import uuid

from django.db import models

from postgres.fields import uuid_field, json_field, interval_field
from postgres.fields import range_fields
from postgres.fields import CompositeType, composite_type_factory


class JSONFieldModel(models.Model):
    json = json_field.JSONField()

    def __unicode__(self):
        return json.dumps(self.json)


class JSONFieldNullModel(models.Model):
    json = json_field.JSONField(null=True)

    def __unicode__(self):
        return json.dumps(self.json)


class UUIDFieldModel(models.Model):
    uuid = uuid_field.UUIDField(default=uuid.uuid4)

    def __unicode__(self):
        return unicode(self.uuid)


class UUIDFieldPKModel(models.Model):
    uuid = uuid_field.UUIDField(primary_key=True, default=uuid.uuid4)

    def __unicode__(self):
        return unicode(self.uuid)


class IntervalFieldModel(models.Model):
    interval = interval_field.IntervalField()


class RangeFieldsModel(models.Model):
    date_range = range_fields.DateRangeField(default='(,)')
    datetime_range = range_fields.DateTimeRangeField(default='(,)')
    int4_range = range_fields.Int4RangeField(default='(,)')


class DjangoFieldsModel(models.Model):
    integer = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    decimal = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=5)


class TimeBoolean(CompositeType):
    time = models.TimeField()
    boolean = models.BooleanField()

    db_type = 'time_boolean'

composite_type_factory('Foo', 'foo', time=models.TimeField())


class CompositeFieldModel(models.Model):
    field = TimeBooleanField()
