# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-09 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('action_points', '0005_auto_20180713_0805'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionpoint',
            name='category',
            field=models.CharField(blank=True, choices=[('Invoice and receive reimbursement of ineligible expenditure', 'Invoice and receive reimbursement of ineligible expenditure'), ('Change cash transfer modality (DCT, reimbursement or direct payment)', 'Change cash transfer modality (DCT, reimbursement or direct payment)'), ('IP to incur and report on additional expenditure', 'IP to incur and report on additional expenditure'), ('Review and amend ICE or budget', 'Review and amend ICE or budget'), ('IP to correct FACE form or Statement of Expenditure', 'IP to correct FACE form or Statement of Expenditure'), ('Schedule a programmatic visit', 'Schedule a programmatic visit'), ('Schedule a follow-up spot check', 'Schedule a follow-up spot check'), ('Schedule an audit', 'Schedule an audit'), ('Block future cash transfers', 'Block future cash transfers'), ('Block or mark vendor for deletion', 'Block or mark vendor for deletion'), ('Escalate to Chief of Operations, Dep Rep, or Rep', 'Escalate to Chief of Operations, Dep Rep, or Rep'), ('Escalate to Investigation', 'Escalate to Investigation'), ('Capacity building / Discussion with partner', 'Capacity building / Discussion with partner'), ('Change IP risk rating', 'Change IP risk rating'), ('Other', 'Other')], max_length=100, verbose_name='Category'),
        ),
    ]