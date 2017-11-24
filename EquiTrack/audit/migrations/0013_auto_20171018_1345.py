# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-10-19 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0012_auto_20171017_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='engagement_type',
            field=models.CharField(
                choices=[('audit', 'Audit'), ('ma', 'Micro Accessment'), ('sc', 'Spot Check'), ('sa', 'Special Audit')],
                max_length=10, verbose_name='Engagement type'),
        ),
    ]