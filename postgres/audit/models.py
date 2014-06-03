from django.conf import settings
from django.db import models, connection

import postgres.fields.json_field

known_models = {}

def get_model_from_table(table):
    if not known_models:
        for model in get_models():
            known_models[model.db_table] = model
    
    return known_models[table]


class AuditLogQuerySet(models.QuerySet):
    def for_instance(self, instance):
        pk = {
            'row_data__%s_id' % instance._meta.pk.name: instance.pk
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
    
    event_id = models.IntegerField(primary_key=True)
    action = models.TextField(choices=[
        ('I', 'INSERT'),
        ('U', 'UPDATE'),
        ('D', 'DELETE'),
        ('T', 'TRUNCATE'),
    ])
    table_name = models.TextField()
    timestamp = models.DateTimeField(db_column='action_tstamp_tx')
    row_data = postgres.fields.json_field.JSONField(null=True)
    changed_fields = postgres.fields.json_field.JSONField(null=True)
    app_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    app_ip_address = models.IPAddressField(null=True)
    
    objects = AuditLogQuerySet.as_manager()
    
    class Meta:
        # This signals we should not create tables.
        managed = False
        db_table = '__audit_logged_actions'
    
    @property
    def current_instance(self):
        model = get_model_from_table(self.table_name)
        # Need to get primary key field name from model class.
        pk = model._meta.pk.name
        return model._default_manager.get(pk=self.row_data[pk.name])
    
    @property
    def old_instance(self):
        model = get_model_from_table(self.table_name)
        data = dict(self.row_data)
        if self.action in ['D', 'U']:
            data.update(**self.changed_fields)
            
        return model(**data)


def start_auditing(model):
    cursor = connection.cursor()
    cursor.execute('SELECT __audit_audit_table(%s)', model._meta.db_table)