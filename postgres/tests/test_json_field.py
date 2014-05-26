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
    
    def test_has(self):
        a = JSONFieldModel.objects.create(json={'a': 1})
        b = JSONFieldModel.objects.create(json={'b': 1})
        results = JSONFieldModel.objects.filter(json__has='a')
        self.assertEquals(set([a]), set(results))
    
    def test_in(self):
        a = JSONFieldModel.objects.create(json={'a': 1})
        b = JSONFieldModel.objects.create(json={'b': 1})
        
        results = JSONFieldModel.objects.filter(json__in={'a': 1, 'b': 1})
        self.assertEquals(set([a, b]), set(results))
        
        results = JSONFieldModel.objects.filter(json__in={'a': 1, 'b': 2})
        self.assertEquals(set([a]), set(results))
    
    def test_has_any(self):
        a = JSONFieldModel.objects.create(json={'a': 1})
        b = JSONFieldModel.objects.create(json={'b': 1})
        
        results = JSONFieldModel.objects.filter(json__has_any=['a', 'c'])
        self.assertEquals(set([a]), set(results))
        
    def test_has_all(self):
        a = JSONFieldModel.objects.create(json={'a': 1})
        b = JSONFieldModel.objects.create(json={'b': 1})
        
        results = JSONFieldModel.objects.filter(json__has_all=['a', 'b'])
        self.assertEquals(set([]), set(results))


    def test_element_is(self):
        a = JSONFieldModel.objects.create(json=[{"a":"foo"},{"b":"bar"},{"c":"baz"}])
        b = JSONFieldModel.objects.create(json=[{"a":1},{"b":2},{"c":3}])
        c = JSONFieldModel.objects.create(json=[0,2,4])
        d = JSONFieldModel.objects.create(json={'a': 1, 'b': {'c': [2, 4, 5]}})
        
        results = JSONFieldModel.objects.filter(json__1={'b': 'bar'})
        self.assertEquals(set([a]), set(results))
        
        results = JSONFieldModel.objects.filter(json__0__lt=2)
        self.assertEquals(set([c]), set(results))
        
        results = JSONFieldModel.objects.filter(json__a=1)
        self.assertEquals(set([d]), set(results))
        
        results = JSONFieldModel.objects.filter(json__0_a__gte=2)
        self.assertEquals(0, results.count())
        
        results = JSONFieldModel.objects.filter(json__0_a__gte=1)
        self.assertEquals(set([b]), set(results))