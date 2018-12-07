# Generated by Django 2.0.9 on 2018-10-16 13:19

from django.db import migrations


def migrate_domains(apps, schema_editor):
    Domain = apps.get_model("EquiTrack", "Domain")
    Country = apps.get_model("users", "Country")

    for country in Country.objects.all():
        Domain.objects.get_or_create(domain='{}.etools.unicef.org'.format(country.schema_name), tenant=country)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_middle_name'),
        ('EquiTrack', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_domains, reverse_code=migrations.RunPython.noop),
    ]
