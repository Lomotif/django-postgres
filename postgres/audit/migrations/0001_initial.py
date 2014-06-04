import os

from django.conf import settings
from django.db import models, migrations

json_ops = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'json_ops.sql')
audit_trigger = os.path.join(os.path.dirname(__file__), '..', 'sql', 'audit_trigger.sql')

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.RunSQL(
            sql=open(json_ops).read().replace('%', '%%'),
        ),
        migrations.RunSQL(
            sql=open(audit_trigger).read().replace('%', '%%'),
            reverse_sql='DROP TABLE __audit_logged_actions'
        ),
    ]