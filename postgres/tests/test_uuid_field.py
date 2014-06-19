from __future__ import unicode_literals

import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from postgres.fields import uuid_field
from .models import UUIDFieldModel, UUIDFieldPKModel

class TestUUIDField(TestCase):
    def test_uuid_field_in_model(self):
        created = UUIDFieldModel.objects.create()
        fetched = UUIDFieldModel.objects.get(uuid=created.uuid)

    def test_uuid_field_as_pk(self):
        created = UUIDFieldPKModel.objects.create()
        fetched = UUIDFieldPKModel.objects.get(pk=created.uuid)

    def test_uuid_field_subfield_base(self):
        obj = UUIDFieldModel()
        obj.uuid = 'b36a53cb610c4ff6ade73f1be0c4b750'
        self.assertTrue(isinstance(obj.uuid, uuid.UUID))
        with self.assertRaises(ValidationError):
            obj.uuid = 'unicode_literals'