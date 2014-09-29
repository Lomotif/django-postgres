import django
from django.db import models

try:
    from ..lookups import PostgresLookup
except ImportError:
    pass

class TSVectorField(models.Field):

    def db_type(self, connection):
        return 'tsvector'


class TSQueryField(models.Field):
    def db_type(self, connection):
        return 'tsquery'


if django.VERSION > (1,7):

    class TSVectorMatches(PostgresLookup):
        lookup_name = 'matches'
        operator = '@@'

    TSVectorField.register_lookup(TSVectorMatches)
