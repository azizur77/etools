from rest_framework import serializers

from partners.models import InterventionResultLink
from partners.serializers.interventions_v2 import InterventionCreateUpdateSerializer
from tpm.models import TPMVisit, TPMPermission, TPMActivity, TPMVisitReportRejectComment, \
    TPMActivityActionPoint
from tpm.serializers.attachments import TPMAttachmentsSerializer, TPMReportAttachmentsSerializer
from utils.permissions.serializers import StatusPermissionsBasedSerializerMixin, \
    StatusPermissionsBasedRootSerializerMixin
from utils.common.serializers.fields import SeparatedReadWriteField
from tpm.serializers.partner import TPMPartnerLightSerializer
from users.serializers import MinimalUserSerializer
from utils.writable_serializers.serializers import WritableNestedSerializerMixin
from users.serializers import SectionSerializer
from locations.serializers import LocationSerializer
from reports.serializers.v1 import ResultSerializer


class TPMPermissionsBasedSerializerMixin(StatusPermissionsBasedSerializerMixin):
    class Meta(StatusPermissionsBasedSerializerMixin.Meta):
        permission_class = TPMPermission


class InterventionResultLinkVisitSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="cp_output.name")

    class Meta:
        model = InterventionResultLink
        fields = [
            'id', 'name'
        ]


class TPMVisitReportRejectCommentSerializer(TPMPermissionsBasedSerializerMixin,
                                            WritableNestedSerializerMixin,
                                            serializers.ModelSerializer):
    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMVisitReportRejectComment
        fields = ['id', 'rejected_at', 'reject_reason', ]


class TPMActivityActionPointSerializer(TPMPermissionsBasedSerializerMixin,
                                       WritableNestedSerializerMixin,
                                       serializers.ModelSerializer):
    section = SeparatedReadWriteField(
        read_field=SectionSerializer(read_only=True),
        required=True
    )

    cp_outputs = SeparatedReadWriteField(
        read_field=ResultSerializer(many=True, read_only=True),
        required=True
    )

    locations = SeparatedReadWriteField(
        read_field=LocationSerializer(many=True, read_only=True)
    )

    person_responsible = SeparatedReadWriteField(
        read_field=MinimalUserSerializer(read_only=True, many=True),
        required=True
    )

    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMActivityActionPoint
        fields = [
            'id', 'section', 'cp_outputs', 'locations', 'person_responsible',
            'due_date', 'status', 'description', 'completed_at', 'actions_taken',
            'follow_up'
        ]

    def create(self, validated_data):
        validated_data['author'] = self.get_user()
        return super(TPMActivityActionPointSerializer, self).create(validated_data)

    def validate(self, data):
        validated_data = super(TPMActivityActionPointSerializer, self).validate(data)

        tpm_visit = self.context['instance']

        section = validated_data.get('section', None) or self.instance.section
        if section not in tpm_visit.sections.all():
            raise serializers.ValidationError({
                "section": "Section doesn't connected with visit"
            })

        return validated_data


class TPMActivitySerializer(TPMPermissionsBasedSerializerMixin, WritableNestedSerializerMixin,
                            serializers.ModelSerializer):
    partnership = SeparatedReadWriteField(
        read_field=InterventionCreateUpdateSerializer(read_only=True),
    )

    cp_output = SeparatedReadWriteField(
        read_field=ResultSerializer(read_only=True),
        required=True
    )

    locations = SeparatedReadWriteField(
        read_field=LocationSerializer(many=True, read_only=True),
    )

    action_points = TPMActivityActionPointSerializer(many=True, required=False)

    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMActivity
        fields = ['id', 'partnership', 'cp_output', 'locations', 'action_points', ]


class TPMVisitLightSerializer(StatusPermissionsBasedRootSerializerMixin, WritableNestedSerializerMixin,
                              serializers.ModelSerializer):
    tpm_activities = TPMActivitySerializer(many=True, required=False)

    tpm_partner = SeparatedReadWriteField(
        read_field=TPMPartnerLightSerializer(read_only=True),
    )

    status_date = serializers.ReadOnlyField()

    class Meta(StatusPermissionsBasedRootSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMVisit
        permission_class = TPMPermission
        fields = [
            'id', 'start_date', 'end_date',
            'tpm_activities', 'tpm_partner',
            'status', 'status_date', 'reference_number',
            'date_created', 'date_of_assigned', 'date_of_tpm_accepted',
            'date_of_tpm_rejected', 'date_of_tpm_reported', 'date_of_unicef_approved',
            'date_of_tpm_report_rejected', 'date_of_cancelled'
        ]


class TPMVisitSerializer(TPMVisitLightSerializer):
    attachments = TPMAttachmentsSerializer(many=True, required=False)
    report = TPMReportAttachmentsSerializer(many=True, required=False)

    unicef_focal_points = SeparatedReadWriteField(
        read_field=MinimalUserSerializer(read_only=True, many=True),
        required=True
    )

    sections = SeparatedReadWriteField(
        read_field=SectionSerializer(read_only=True, many=True),
        required=True
    )

    report_reject_comments = SeparatedReadWriteField(
        read_field=TPMVisitReportRejectCommentSerializer(many=True, read_only=True),
    )

    class Meta(TPMVisitLightSerializer.Meta):
        fields = TPMVisitLightSerializer.Meta.fields + [
            'reject_comment',
            'attachments',
            'report',
            'unicef_focal_points',
            'sections',
            'report_reject_comments',
        ]
        extra_kwargs = {
            'tpm_partner': {'required': True},
        }


class TPMVisitDraftSerializer(TPMVisitSerializer):
    class Meta(TPMVisitSerializer.Meta):
        extra_kwargs = {
            'tpm_partner': {'required': False},
        }
