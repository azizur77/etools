# Generated by Django 2.0.9 on 2018-12-29 02:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import etools.applications.reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0013_auto_20180709_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appliedindicator',
            name='baseline',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=etools.applications.reports.models.indicator_default_dict, null=True),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='target',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=etools.applications.reports.models.indicator_default_dict),
        ),
    ]
