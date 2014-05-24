from __future__ import unicode_literals

import json
import decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six

from psycopg2.extras import register_json

# Actually register jsonb!
# http://schinckel.net/2014/05/24/python%2C-postgres-and-jsonb/
register_json(oid=3802, array_oid=3807)


    

class JSONField(six.with_metaclass(models.SubfieldBase, models.Field)):
    description = 'JSON Field'
    
    def __init__(self, *args, **kwargs):
        self.decode_kwargs = kwargs.pop('decode_kwargs', {
            'parse_float': decimal.Decimal
        })
        self.encode_kwargs = kwargs.pop('encode_kwargs', {
            'default': default
        })
        super(JSONField, self).__init__(*args, **kwargs)
    
    def get_internal_type(self):
        return 'JSONField'
    
    def db_type(self, connection):
        return 'jsonb'

    def get_db_prep_value(self, value, connection=None, prepared=None):
        return self.get_prep_value(value)
    
    def get_prep_value(self, value):
        if value is None:
            if not self.null and self.blank:
                return ""
            return None
        return json.dumps(value, **self.encode_kwargs)
    
    def get_prep_lookup(self, lookup_type, value, prepared=False):
        if lookup_type == 'has_key':
            # Need to ensure we have a string, as no other
            # values is appropriate.
            if not isinstance(value, six.string_types):
                value = '%s' % value
        if lookup_type in ['all_keys', 'any_keys']:
            if isinstance(value, six.string_types):
                value = [value]
            # This will cast numbers to strings, but also grab the keys
            # from a dict.
            value = ['%s' % v for v in value]
                
        return value
    
    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if lookup_type in ['contains', 'in']:
            value = self.get_prep_value(value)
            return [value]
        
        return super(JSONField, self).get_db_prep_lookup(lookup_type, value, connection, prepared)
        
    def to_python(self, value):
        if isinstance(value, six.string_types) or value is None:
            if not value:
                if self.blank:
                    return ''
                return None
            try:
                return json.loads(value, **self.decode_kwargs)
            except ValueError as exc:
                raise ValidationError(*exc.args)
        
        # Should we round-trip a value when it is assigned?
        # It means we will always have data in the format that
        # it will come back from the server, which is a good
        # thing.
        return self.to_python(self.get_prep_value(value))


from django.db.models.lookups import BuiltinLookup, Lookup

class PostgresLookup(BuiltinLookup):
    def process_lhs(self, qn, connection, lhs=None):
        lhs = lhs or self.lhs
        return qn.compile(lhs)
    
    def get_rhs_op(self, connection, rhs):
        return '%s %s' % (self.operator, rhs)

class HasKey(PostgresLookup):
    lookup_name = 'has_key'
    operator = '?'

JSONField.register_lookup(HasKey)


class Contains(PostgresLookup):
    lookup_name = 'contains'
    operator = '@>'
    
JSONField.register_lookup(Contains)

class In(PostgresLookup):
    lookup_name = 'in'
    operator = '<@'

JSONField.register_lookup(In)

class AllKeys(PostgresLookup):
    lookup_name = 'all_keys'
    operator = '?&'

JSONField.register_lookup(AllKeys)

class AnyKeys(PostgresLookup):
    lookup_name = 'any_keys'
    operator = '?|'

JSONField.register_lookup(AnyKeys)


def default(o):
    if hasattr(o, 'to_json'):
        return o.to_json()
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, datetime.datetime):
        if o.tzinfo:
            return o.strftime('%Y-%m-%dT%H:%M:%S%z')
        return o.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(o, datetime.date):
        return o.strftime("%Y-%m-%d")
    if isinstance(o, datetime.time):
        if o.tzinfo:
            return o.strftime('%H:%M:%S%z')
        return o.strftime("%H:%M:%S")
    
    raise TypeError(repr(o) + " is not JSON serializable")