# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-09-28 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0008_auto_20170921_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='item_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='PO Item Number'),
        ),
    ]
