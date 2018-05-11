from django.utils.translation import ugettext_lazy as _

from django_comments.models import Comment
from rest_framework import serializers

from etools.applications.action_points.models import ActionPoint
from etools.applications.EquiTrack.serializers import SnapshotModelSerializer
from etools.applications.locations.serializers import LocationLightSerializer
from etools.applications.partners.serializers.interventions_v2 import InterventionCreateUpdateSerializer
from etools.applications.partners.serializers.partner_organization_v2 import MinimalPartnerOrganizationListSerializer
from etools.applications.permissions2.serializers import PermissionsBasedSerializerMixin
from etools.applications.reports.serializers.v1 import ResultSerializer
from etools.applications.snapshot.serializers import ActivitySerializer
from etools.applications.users.models import Section
from etools.applications.users.serializers import OfficeSerializer
from etools.applications.users.serializers_v3 import MinimalUserSerializer
from etools.applications.utils.common.serializers.fields import SeparatedReadWriteField
from etools.applications.utils.common.serializers.mixins import UserContextSerializerMixin


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name')


class ActionPointLightSerializer(UserContextSerializerMixin,
                                 PermissionsBasedSerializerMixin,
                                 SnapshotModelSerializer,
                                 serializers.ModelSerializer):
    related_module = serializers.ReadOnlyField(label=_('Related Module'))
    reference_number = serializers.ReadOnlyField(label=_('Reference Number'))

    author = MinimalUserSerializer(read_only=True, label=_('Author'))
    assigned_by = MinimalUserSerializer(read_only=True, label=_('Assigned By'))
    assigned_to = SeparatedReadWriteField(
        read_field=MinimalUserSerializer(read_only=True, label=_('Assigned To')),
        required=True
    )

    partner = SeparatedReadWriteField(
        read_field=MinimalPartnerOrganizationListSerializer(read_only=True, label=_('Partner')),
    )
    intervention = SeparatedReadWriteField(
        read_field=InterventionCreateUpdateSerializer(read_only=True, label=_('PD/SSFA')),
        required=False,
    )

    cp_output = SeparatedReadWriteField(
        read_field=ResultSerializer(read_only=True, label=_('CP Output')),
        required=False,
    )

    location = SeparatedReadWriteField(
        read_field=LocationLightSerializer(read_only=True, label=_('Location')),
    )

    section = SeparatedReadWriteField(
        read_field=SectionSerializer(read_only=True, label=_('Section')),
        required=True,
    )
    office = SeparatedReadWriteField(
        read_field=OfficeSerializer(read_only=True, label=_('Office')),
        required=True
    )
    status_date = serializers.DateTimeField(read_only=True, label=_('Status Date'))

    class Meta:
        model = ActionPoint
        fields = [
            'id', 'reference_number', 'related_module',
            'author', 'assigned_by', 'assigned_to',

            'section', 'office', 'location',
            'partner', 'cp_output', 'intervention',

            'priority', 'due_date', 'description', 'action_taken',

            'created', 'date_of_completion',
            'status', 'status_date',
        ]


class CommentSerializer(UserContextSerializerMixin,
                        serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True, label=_('Author'))

    class Meta:
        model = Comment
        fields = (
            'id', 'user', 'comment', 'submit_date'
        )
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['user'] = self.get_user()
        return super(CommentSerializer, self).create(validated_data)


class ActionPointSerializer(ActionPointLightSerializer):
    comments = CommentSerializer(many=True, label=_('Comments'))
    history = ActivitySerializer(many=True, label=_('History'))

    related_object_str = serializers.SerializerMethodField(label=_('Reference'))
    related_object_url = serializers.SerializerMethodField()

    class Meta(ActionPointLightSerializer.Meta):
        fields = ActionPointLightSerializer.Meta.fields + [
            'comments', 'history', 'related_object_str', 'related_object_url',
        ]
        extra_kwargs = {
            'author': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['author'] = self.get_user()
        validated_data['assigned_by'] = self.get_user()

        return super(ActionPointSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'assigned_to' in validated_data:
            validated_data['assigned_by'] = self.get_user()

        return super(ActionPointSerializer, self).update(instance, validated_data)

    def get_related_object_str(self, obj):
        return str(obj.related_object) if obj.related_object else None

    def get_related_object_url(self, obj):
        return obj.related_object.get_object_url() if obj.related_object else None
