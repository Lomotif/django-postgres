from django.conf import settings
from django.db import models, connection

import postgres.fields.json_field
import postgres.fields.internal_types
import postgres.fields.bigint_field

known_models = {}

def get_model_from_table(table):
    if not known_models:
        for model in models.get_models():
            known_models[model._meta.db_table] = model
    
    return known_models[table]


class AuditLogQuerySet(models.QuerySet):
    def for_instance(self, instance):
        pk = {
            'row_data__%s' % instance._meta.pk.name: instance.pk
        }
        return self.filter(
            table_name=instance._meta.db_table,
            **pk
        )
    
    def inserts(self):
        return self.filter(action='I')
    
    def updates(self):
        return self.filter(action='U')
    
    def deletes(self):
        return self.filter(action='D')
    
    def after(self, when):
        return self.filter(timestamp__gt=when)
    
    def before(self, when):
        return self.filter(timestamp__lt=when)
    
    def between(self, start, finish):
        return self.before(finish).after(start)
    
    def by_user(self, user):
        return self.filter(app_user=user.pk)
    



class AuditLog(models.Model):
    """
    This is really only for being able to access the data,
    we shouldn't use it for saving. Perhaps we could have the
    underlying system create a read-only view so any saves fail.
    """
    
    action = models.TextField(choices=[
        ('I', 'INSERT'),
        ('U', 'UPDATE'),
        ('D', 'DELETE'),
        ('T', 'TRUNCATE'),
    ], db_index=True)
    table_name = models.TextField()
    relid = postgres.fields.internal_types.OIDField()
    timestamp = models.DateTimeField()
    transaction_id = postgres.fields.bigint_field.BigIntField(null=True)
    client_query = models.TextField()
    statement_only = models.BooleanField(default=False)
    row_data = postgres.fields.json_field.JSONField(null=True)
    changed_fields = postgres.fields.json_field.JSONField(null=True)
    app_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    app_ip_address = models.IPAddressField(null=True)
    
    objects = AuditLogQuerySet.as_manager()
    
    @property
    def current_instance(self):
        model = get_model_from_table(self.table_name)
        # Need to get primary key field name from model class.
        pk = model._meta.pk
        query = 'SELECT * FROM "%s"."%s" WHERE "%s"=%s' % (
            self.schema_name, self.table_name,
            pk.name, self.row_data[pk.name]
        )
        return model._default_manager.raw(query)[0]
    
    @property
    def old_instance(self):
        # Generate a copy of what the instance looked like before this
        # event (in the case of a delete or update), or after the event
        # in the case of a create.
        model = get_model_from_table(self.table_name)
        data = dict(self.row_data)
        if self.action in ['D', 'U']:
            data.update(**self.changed_fields)
            # Remap db_column to django field name.
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)
            if field.rel:
                db_column = field.db_column or (field.name + '_id')
                # What if this instance doesn't exist?
                data[field.name] = field.rel.to.objects.get(pk=data.pop(db_column))
            elif field.db_column:
                data[field.name] = data.pop(field.db_column)
        
        data = dict((key,value) for (key,value) in data.items() if key in fields)
        
        return model(**data)
