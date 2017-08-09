# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-05-17 20:17
from __future__ import unicode_literals
from django.db import migrations, models


def reverse(apps, schema_editor):
    pass


def migrate_cps(apps, schema_editor):
    CountryProgramme = apps.get_model('reports', 'CountryProgramme')
    Agreement = apps.get_model('partners', 'Agreement')
    Intervention = apps.get_model('partners', 'Intervention')
    cps = CountryProgramme.objects.filter(invalid=False, wbs__contains='/A0/')
    for cp in cps:
        agreements = Agreement.objects.filter(start__gte=cp.from_date,
                                              start__lte=cp.to_date,).exclude(
                                              agreement_type__in=['MOU']).update(country_programme=cp)

        mou_agreements = Agreement.objects.filter(country_programme__isnull=False,
                                                  agreement_type__in=['MOU']).update(country_programme=None)

        interventions = Intervention.objects.filter(start__gte=cp.from_date,
                                                    start__lte=cp.to_date,)
        for intervention in interventions:
            wrong_cp = []
            for rl in intervention.result_links.all():
                if rl.cp_output.country_programme != cp:
                    wrong_cp.append(rl.cp_output.wbs)
            if len(wrong_cp) > 0:
                # raise BaseException("PD [{}] STATUS [{}] CP [{}] has wrongly mapped outputs {}".format(
                #     intervention.id, intervention.status, cp.wbs, wrong_cp))
                print ("PD [P{}] STATUS [{}] CP [{}] has wrongly mapped outputs {}".format(intervention.id, intervention.status, cp.wbs, wrong_cp))
            intervention.country_programme = cp
            intervention.save()


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0037_auto_20170627_1854'),
        ('reports', '0011_auto_20170614_1831')
    ]

    operations = [
        # This is required or 'apps.get_model' will fail in the end
        migrations.AlterModelManagers(
            name='agreement',
            managers=[
            ],
        ),

        migrations.RunPython(
            migrate_cps, reverse_code=reverse),

        migrations.AlterModelManagers(
            name='agreement',
            managers=[
                ('view_objects', models.manager.Manager()),
            ],
        ),
    ]