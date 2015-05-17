from django.db import models

from postgres.fields.composite_field import composite_type_factory, CompositeType


class TimeBoolean(CompositeType):
    time = models.TimeField()
    boolean = models.BooleanField()

    db_type = 'time_boolean'

composite_type_factory('Foo', 'foo', time=models.TimeField())
