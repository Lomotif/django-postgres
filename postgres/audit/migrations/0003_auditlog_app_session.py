# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='app_session',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
