import os

from django.conf import settings
from django.db import migrations

json_ops = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'json', 'jsonb_subtract.sql')
if_modified = os.path.join(os.path.dirname(__file__), '..', 'sql', 'if_modified.sql')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.RunSQL(
            sql=open(json_ops).read().replace('%', '%%'),
        ),
        migrations.RunSQL(
            sql=open(if_modified).read().replace('%', '%%'),
            reverse_sql='DROP FUNCTION __audit.if_modified_func'
        ),
    ]
