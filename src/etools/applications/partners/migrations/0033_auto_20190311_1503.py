# Generated by Django 2.1.5 on 2019-03-11 15:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0032_auto_20190301_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interventionamendment',
            name='types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('admin_error', 'Administrative error (correction)'), ('budget_lte_20', 'Budget <= 20%'), ('budget_gt_20', 'Budget > 20'), ('change', 'Changes to planned results'), ('no_cost', 'No cost extension'), ('other', 'Other'), ('dates', 'Dates'), ('results', 'Results'), ('budget', 'Budget')], max_length=50, verbose_name='Types'), size=None),
        ),
    ]
