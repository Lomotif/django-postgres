from __future__ import unicode_literals

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from psycopg2.extras import DateRange, DateTimeRange, NumericRange

from postgres.fields import range_fields

from .models import RangeFieldsModel, DjangoFieldsModel

class TestRangeFields(TestCase):
    def test_range_fields_in_model(self):
        created = RangeFieldsModel.objects.create()
        fetched = RangeFieldsModel.objects.get()


class TestRangeFieldLookups(TestCase):
    def test_int4_range_lookups(self):
        pass


class TestDjangoFieldLookupsWithRange(TestCase):
    def test_int4_range_lookups(self):
        _0 = DjangoFieldsModel.objects.create(integer=0)
        _10 = DjangoFieldsModel.objects.create(integer=10)
        _20 = DjangoFieldsModel.objects.create(integer=20)
        _100 = DjangoFieldsModel.objects.create(integer=100)

        result = DjangoFieldsModel.objects.filter(integer__in=NumericRange(lower=1, upper=20, bounds='[]'))
        self.assertEquals(set([_10, _20]), set(result))

        result = DjangoFieldsModel.objects.filter(integer__in='[1,20]')
        self.assertEquals(set([_10, _20]), set(result))