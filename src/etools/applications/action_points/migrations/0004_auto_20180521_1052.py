# Generated by Django 1.10.8 on 2018-05-21 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('action_points', '0003_auto_20180518_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionpoint',
            name='engagement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_points', to='audit.Engagement', verbose_name='Engagement'),
        ),
        migrations.AlterField(
            model_name='actionpoint',
            name='tpm_activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_points', to='tpm.TPMActivity', verbose_name='TPM Activity'),
        ),
    ]
