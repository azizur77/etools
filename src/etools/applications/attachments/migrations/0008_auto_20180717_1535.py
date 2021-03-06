# Generated by Django 1.10.8 on 2018-07-17 15:35
from __future__ import unicode_literals

from django.db import migrations


def migrate_core_value_assessment(apps, schema_editor):
    Attachment = apps.get_model('attachments', 'Attachment')
    PartnerOrganization = apps.get_model('partners', 'PartnerOrganization')
    attachments = Attachment.objects.filter(content_type__app_label='partners',
                                            content_type__model='partnerorganization',
                                            code='partners_partner_assessment')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    cva_ct = ContentType.objects.get(app_label='partners', model='corevaluesassessment')
    for attachment in attachments:
        partner = PartnerOrganization.objects.get(pk=attachment.object_id)
        assert partner.core_values_assessments.count() == 1
        cva = partner.core_values_assessments.first()
        attachment.object_id = cva.id
        attachment.content_type = cva_ct
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0007_auto_20180322_1723'),
        ('partners', '0018_auto_20180717_1536'),
    ]

    operations = [
        migrations.RunPython(migrate_core_value_assessment, migrations.RunPython.noop)
    ]
