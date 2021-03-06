from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from django.db.models import signals

import factory
from factory.fuzzy import FuzzyText

from etools.applications.core.tests.cases import SCHEMA_NAME
from etools.applications.users import models
from etools.applications.publics.tests.factories import PublicsCurrencyFactory


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = "Partnership Manager"


class OfficeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Office

    name = 'An Office'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = super()._create(model_class, *args, **kwargs)

        if hasattr(connection.tenant, 'id') and connection.tenant.schema_name != 'public':
            connection.tenant.offices.add(obj)

        return obj


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Country
        django_get_or_create = ('schema_name',)

    name = "Test Country"
    schema_name = SCHEMA_NAME
    local_currency = factory.SubFactory(PublicsCurrencyFactory)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserProfile
        django_get_or_create = ('user',)

    country = factory.SubFactory(CountryFactory)
    office = factory.SubFactory(OfficeFactory)
    job_title = 'Chief Tester'
    phone_number = '0123456789'
    partner_staff_member = None
    # We pass in profile=None to prevent UserFactory from creating another profile
    # (this disables the RelatedFactory)
    user = factory.SubFactory('etools.applications.users.tests.factories.UserFactory', profile=None)

    @factory.post_generation
    def countries_available(self, create, extracted, **kwargs):
        if extracted is not None:
            for country in extracted:
                self.countries_available.add(country)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = FuzzyText()
    email = factory.Sequence(lambda n: "user{}@example.com".format(n))
    password = factory.PostGenerationMethodCall('set_password', 'test')

    # unicef user is set as group by default, but we can easily overwrite it by passing empty list
    groups__data = ['UNICEF User']

    # We pass in 'user' to link the generated Profile to our just-generated User
    # This will call ProfileFactory(user=our_new_user), thus skipping the SubFactory.
    profile = factory.RelatedFactory(ProfileFactory, 'user')

    @factory.post_generation
    def groups(self, create, extracted, data=None, **kwargs):
        if not create:
            return

        extracted = (extracted or []) + (data or [])

        if extracted:
            for i, group in enumerate(extracted):
                if isinstance(group, str):
                    extracted[i] = Group.objects.get_or_create(name=group)[0]

            self.groups.add(*extracted)


class SimpleUserFactory(UserFactory):
    groups__data = []


class PMEUserFactory(UserFactory):
    groups__data = ['UNICEF User', 'PME']
