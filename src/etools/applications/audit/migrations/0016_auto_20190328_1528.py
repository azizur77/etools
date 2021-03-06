# Generated by Django 2.1.7 on 2019-03-28 15:28

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0015_auto_20190312_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='status',
            field=django_fsm.FSMField(choices=[('partner_contacted', 'IP Contacted'), ('report_submitted', 'Report Submitted'), ('final', 'Final Report'), ('cancelled', 'Cancelled')], default='partner_contacted', max_length=30, verbose_name='Status'),
        ),
    ]
