from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.test import TestCase

from postgres.fields import json_field
from .models import JSONFieldModel, JSONFieldNullModel

class TestJSONField(TestCase):
    def test_json_field_in_model(self):
        created = JSONFieldModel.objects.create(json={'foo': 'bar'})
        fetched = JSONFieldModel.objects.get()
        
        self.assertEquals({'foo': 'bar'}, fetched.json)
    
    def test_subfield_base(self):
        obj = JSONFieldModel()
        obj.json = '{"foo": "bar"}'
        self.assertEquals({'foo': 'bar'}, obj.json)
        
        with self.assertRaises(ValidationError):
            obj.json = '{"foo":}'
        
        obj.json = '["foo", "bar"]'
        self.assertEquals(['foo', 'bar'], obj.json)

class TestJSONFieldLookups(TestCase):
    def test_exact(self):
        JSONFieldModel.objects.create(json={})
        JSONFieldModel.objects.create(json={'foo': 'bar'})
        self.assertEquals(2, JSONFieldModel.objects.all().count())
        self.assertEquals(1, JSONFieldModel.objects.exclude(json={}).count())
        self.assertEquals(1, JSONFieldModel.objects.filter(json={}).count())
        self.assertEquals(1, JSONFieldModel.objects.filter(json={'foo':'bar'}).count())
    
    def test_contains(self):
        JSONFieldModel.objects.create(json={})
        JSONFieldModel.objects.create(json={'foo':'bar'})
        self.assertEquals(1, JSONFieldModel.objects.filter(json__contains={'foo':'bar'}).count())
        JSONFieldModel.objects.create(json={'foo':'bar', 'baz':'bing'})
        self.assertEquals(2, JSONFieldModel.objects.filter(json__contains={'foo':'bar'}).count())
        self.assertEquals(1, JSONFieldModel.objects.filter(json__contains={'baz':'bing', 'foo':'bar'}).count())
    
    def test_isnull(self):
        JSONFieldNullModel.objects.create(json=None)
        JSONFieldNullModel.objects.create(json={})
        JSONFieldNullModel.objects.create(json={'foo':'bar'})

        self.assertEquals(1, JSONFieldNullModel.objects.filter(json=None).count())
        self.assertEquals(None, JSONFieldNullModel.objects.get(json=None).json)
    
    def test_has_key(self):
        a = JSONFieldModel.objects.create(json={'a': 1})
        b = JSONFieldModel.objects.create(json={'b': 1})
        results = JSONFieldModel.objects.filter(json__has_key='a')
        self.assertEquals(set([a]), set(results))