# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-10 08:37
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0004_make_not_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagement',
            name='exchange_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20,
                                      null=True, verbose_name='Exchange Rate'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='shared_ip_with',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('DPKO', 'DPKO'), ('ECA', 'ECA'), ('ECLAC', 'ECLAC'), ('ESCWA', 'ESCWA'), ('FAO', 'FAO'), ('ILO', 'ILO'), ('IOM', 'IOM'), ('OHCHR', 'OHCHR'), ('UN', 'UN'), ('UN Women', 'UN Women'), ('UNAIDS', 'UNAIDS'), ('UNDP', 'UNDP'), (
                'UNESCO', 'UNESCO'), ('UNFPA', 'UNFPA'), ('UN - Habitat', 'UN - Habitat'), ('UNHCR', 'UNHCR'), ('UNODC', 'UNODC'), ('UNOPS', 'UNOPS'), ('UNRWA', 'UNRWA'), ('UNSC', 'UNSC'), ('UNU', 'UNU'), ('WB', 'WB'), ('WFP', 'WFP'), ('WHO', 'WHO')], max_length=20), blank=True, default=[], size=None, verbose_name='Shared Audit with'),
        ),
        migrations.AlterField(
            model_name='finding',
            name='recommendation',
            field=models.TextField(blank=True, verbose_name='Finding and Recommendation'),
        ),
    ]
