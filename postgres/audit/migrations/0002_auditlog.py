# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import postgres.fields.internal_types
import postgres.fields.bigint_field
import postgres.fields.json_field


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.TextField(db_index=True, choices=[(b'I', b'INSERT'), (b'U', b'UPDATE'), (b'D', b'DELETE'), (b'T', b'TRUNCATE')])),
                ('table_name', models.TextField()),
                ('relid', postgres.fields.internal_types.OIDField(editable=False, db_index=True)),
                ('timestamp', models.DateTimeField()),
                ('transaction_id', postgres.fields.bigint_field.BigIntField(null=True)),
                ('client_query', models.TextField()),
                ('statement_only', models.BooleanField(default=False)),
                ('row_data', postgres.fields.json_field.JSONField(null=True)),
                ('changed_fields', postgres.fields.json_field.JSONField(null=True)),
                ('app_ip_address', models.IPAddressField(null=True)),
                ('app_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
