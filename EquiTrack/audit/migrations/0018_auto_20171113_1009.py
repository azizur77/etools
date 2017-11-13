# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-11-13 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0017_auto_20171031_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='shared_ip_with',
            field=models.CharField(blank=True, choices=[('DPKO', 'DPKO'), ('ECA', 'ECA'), ('ECLAC', 'ECLAC'), ('ESCWA', 'ESCWA'), ('FAO', 'FAO'), ('ILO', 'ILO'), ('IOM', 'IOM'), ('OHCHR', 'OHCHR'), ('UN', 'UN'), ('UN Women', 'UN Women'), ('UNAIDS', 'UNAIDS'), ('UNDP', 'UNDP'), ('UNESCO', 'UNESCO'), ('UNFPA', 'UNFPA'), ('UN - Habitat', 'UN - Habitat'), ('UNHCR', 'UNHCR'), ('UNODC', 'UNODC'), ('UNOPS', 'UNOPS'), ('UNRWA', 'UNRWA'), ('UNSC', 'UNSC'), ('UNU', 'UNU'), ('WB', 'WB'), ('WFP', 'WFP'), ('WHO', 'WHO')], max_length=20, verbose_name='Shared IP with'),
        ),
    ]
