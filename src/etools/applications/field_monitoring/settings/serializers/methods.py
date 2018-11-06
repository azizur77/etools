from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from etools.applications.field_monitoring.settings.models import MethodType
from etools.applications.field_monitoring.shared.models import Method


class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ('id', 'name', 'is_types_applicable')


class MethodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MethodType
        fields = ('id', 'method', 'name')

    def validate_method(self, method):
        try:
            self.Meta.model.clean_method(method)
        except DjangoValidationError as ex:
            raise ValidationError(ex.message)

        return method

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        if not validated_data['method'].is_types_applicable:
            raise ValidationError({'method', _('Unable to add type for this Method')})

        return validated_data
