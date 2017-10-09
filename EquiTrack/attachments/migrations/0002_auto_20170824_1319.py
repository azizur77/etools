# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-24 13:19
from __future__ import unicode_literals

import attachments.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=attachments.models.generate_file_path),
        ),
    ]
