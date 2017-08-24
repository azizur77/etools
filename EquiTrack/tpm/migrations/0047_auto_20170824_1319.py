# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-24 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tpm', '0046_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tpmactivity',
            options={'ordering': ['tpm_visit', 'id'], 'verbose_name_plural': 'TPM Activities'},
        ),
        migrations.AlterModelOptions(
            name='tpmactivityactionpoint',
            options={'ordering': ['tpm_activity', 'id']},
        ),
        migrations.AlterModelOptions(
            name='tpmvisitreportrejectcomment',
            options={'ordering': ['tpm_visit', 'id'], 'verbose_name_plural': 'Report Reject Comments'},
        ),
        migrations.AlterField(
            model_name='tpmvisitreportrejectcomment',
            name='rejected_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
