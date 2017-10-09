# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-10-02 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm


def update_action_points_choices(apps, schema_editor):
    apps.get_model('audit', 'EngagementActionPoint').objects\
        .filter(description='Invoice and recieve reimbursement of ineligible expenditure')\
        .update(description='Invoice and receive reimbursement of ineligible expenditure')


def do_nothing(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0009_purchaseorder_item_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='date_of_cancel',
            field=models.DateField(blank=True, null=True, verbose_name='Date report cancelled'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_comments_by_ip',
            field=models.DateField(blank=True, null=True, verbose_name='Date comments received from IP'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_comments_by_unicef',
            field=models.DateField(blank=True, null=True, verbose_name='Date comments received from UNICEF'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_draft_report_to_ip',
            field=models.DateField(blank=True, null=True, verbose_name='Date draft report issued to IP'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_draft_report_to_unicef',
            field=models.DateField(blank=True, null=True, verbose_name='Date draft report issued to UNICEF'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_field_visit',
            field=models.DateField(blank=True, null=True, verbose_name='Date of field visit'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_final_report',
            field=models.DateField(blank=True, null=True, verbose_name='Date report finalized'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='date_of_report_submit',
            field=models.DateField(blank=True, null=True, verbose_name='Date report submitted'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='partner_contacted_at',
            field=models.DateField(blank=True, null=True, verbose_name='Date IP was contacted'),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='status',
            field=django_fsm.FSMField(choices=[('partner_contacted', 'IP Contacted'), ('report_submitted', 'Report Submitted'), ('final', 'Final Report'), ('cancelled', 'Cancelled')], default='partner_contacted', max_length=30, protected=True, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='engagementactionpoint',
            name='description',
            field=models.CharField(choices=[('Invoice and receive reimbursement of ineligible expenditure', 'Invoice and receive reimbursement of ineligible expenditure'), ('Change cash transfer modality (DCT, reimbursement or direct payment)', 'Change cash transfer modality (DCT, reimbursement or direct payment)'), ('IP to incur and report on additional expenditure', 'IP to incur and report on additional expenditure'), ('Review and amend ICE or budget', 'Review and amend ICE or budget'), ('IP to correct FACE form or Statement of Expenditure', 'IP to correct FACE form or Statement of Expenditure'), ('Schedule a programmatic visit', 'Schedule a programmatic visit'), ('Schedule a follow-up spot check', 'Schedule a follow-up spot check'), ('Schedule an audit', 'Schedule an audit'), ('Block future cash transfers', 'Block future cash transfers'), ('Block or mark vendor for deletion', 'Block or mark vendor for deletion'), ('Escalate to Chief of Operations, Dep Rep, or Rep', 'Escalate to Chief of Operations, Dep Rep, or Rep'), ('Escalate to Investigation', 'Escalate to Investigation'), ('Capacity building / Discussion with partner', 'Capacity building / Discussion with partner'), ('Other', 'Other')], max_length=100),
        ),
        migrations.RunPython(update_action_points_choices, do_nothing),
    ]
