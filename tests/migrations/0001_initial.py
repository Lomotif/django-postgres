# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import postgres.fields.interval_field
import postgres.fields.range_fields
import tests.models
import postgres.fields
import postgres.fields.uuid_field
import postgres.operations
import uuid
import decimal
import django.core.serializers.json


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        postgres.operations.CreateCompositeType(
            name='time_boolean',
            fields=[
                ('time', models.TimeField()),
                ('boolean', models.BooleanField())
            ]
        ),
        migrations.CreateModel(
            name='CompositeFieldModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', tests.models.TimeBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='DjangoFieldsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('integer', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('datetime', models.DateTimeField(blank=True, null=True)),
                ('decimal', models.DecimalField(decimal_places=5, blank=True, null=True, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='IntervalFieldModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval', postgres.fields.interval_field.IntervalField()),
            ],
        ),
        migrations.CreateModel(
            name='JSONFieldModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', postgres.fields.JSONField(encode_kwargs={'cls': django.core.serializers.json.DjangoJSONEncoder}, decode_kwargs={'parse_float': decimal.Decimal})),
            ],
        ),
        migrations.CreateModel(
            name='JSONFieldNullModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', postgres.fields.JSONField(encode_kwargs={'cls': django.core.serializers.json.DjangoJSONEncoder}, decode_kwargs={'parse_float': decimal.Decimal}, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RangeFieldsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_range', postgres.fields.range_fields.DateRangeField(default=b'(,)')),
                ('datetime_range', postgres.fields.range_fields.DateTimeRangeField(default=b'(,)')),
                ('int4_range', postgres.fields.range_fields.Int4RangeField(default=b'(,)')),
            ],
        ),
        migrations.CreateModel(
            name='UUIDFieldModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', postgres.fields.uuid_field.UUIDField(default=uuid.uuid4, max_length=36)),
            ],
        ),
        migrations.CreateModel(
            name='UUIDFieldPKModel',
            fields=[
                ('uuid', postgres.fields.uuid_field.UUIDField(default=uuid.uuid4, max_length=36, primary_key=True, serialize=False)),
            ],
        ),
    ]
