# Generated by Django 1.9.10 on 2017-09-07 10:31
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permissions2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='condition',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), blank=True, default=[], size=None),
        ),
    ]
