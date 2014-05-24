from __future__ import unicode_literals

from django.db import models

from postgres.fields import uuid_field

class UUIDFieldModel(models.Model):
    uuid = uuid_field.UUIDField(auto=True)

class UUIDFieldPKModel(models.Model):
    uuid = uuid_field.UUIDField(primary_key=True)