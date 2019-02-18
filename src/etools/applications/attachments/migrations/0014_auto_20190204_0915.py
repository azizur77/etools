# Generated by Django 2.0.9 on 2019-02-04 09:15

from django.db import migrations

def update_internal_prc_review_file_type(apps, schema_editor):
    AttachmentFileType = apps.get_model("unicef_attachments", "filetype")
    try:
        file_type = AttachmentFileType.objects.get(
            code="partners_intervention_amendment_internal_prc_review",
        )
    except AttachmentFileType.DoesNotExist:
        pass
    else:
        file_type.label = "Internal PRC Review"
        file_type.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0013_attachmentflat_pd_ssfa'),
    ]

    operations = [
        migrations.RunPython(
            update_internal_prc_review_file_type,
        )
    ]