from __future__ import unicode_literals

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from postgres.fields import interval_field
from .models import IntervalFieldModel

class TestIntervalField(TestCase):
    def test_interval_field_in_model(self):
        created = IntervalFieldModel.objects.create(interval=timedelta(1))
        fetched = IntervalFieldModel.objects.get(interval=created.interval)

