from __future__ import unicode_literals

import json

from django.db import models

from postgres.fields import uuid_field, json_field, interval_field

class JSONFieldModel(models.Model):
    json = json_field.JSONField()

    def __unicode__(self):
        return json.dumps(self.json)

class JSONFieldNullModel(models.Model):
    json = json_field.JSONField(null=True)

    def __unicode__(self):
        return json.dumps(self.json)

class UUIDFieldModel(models.Model):
    uuid = uuid_field.UUIDField(auto=True)

    def __unicode__(self):
        return unicode(self.uuid)

class UUIDFieldPKModel(models.Model):
    uuid = uuid_field.UUIDField(primary_key=True)

    def __unicode__(self):
        return unicode(self.uuid)


class IntervalFieldModel(models.Model):
    interval = interval_field.IntervalField()