# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-06-14 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase_order', '0004_auditorfirm_unicef_allowed'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditorstaffmember',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
    ]