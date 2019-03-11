# Generated by Django 2.0.9 on 2019-03-01 10:29

from django.db import migrations, models


def update_document_type(apps, schema_editor):
    Intervention = apps.get_model("partners", "intervention")
    Intervention.objects.filter(document_type="SHPD").update(
        document_type="HPD",
    )


def reset_document_type(apps, schema_editor):
    Intervention = apps.get_model("partners", "intervention")
    Intervention.objects.filter(document_type="HPD").update(
        document_type="SHPD",
    )


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0031_auto_20190122_1412'),
    ]

    operations = [
        migrations.RunPython(
            update_document_type,
            reverse_code=reset_document_type,
        ),
        migrations.AlterField(
            model_name='intervention',
            name='document_type',
            field=models.CharField(choices=[('PD', 'Programme Document'), ('HPD', 'Humanitarian Programme Document'), ('SSFA', 'SSFA')], max_length=255, verbose_name='Document Type'),
        ),
    ]