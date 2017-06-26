from django.db.models import Prefetch
from django.http import Http404
from django.views.generic.detail import SingleObjectMixin
from django_filters.rest_framework import DjangoFilterBackend
from easy_pdf.views import PDFTemplateView
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from utils.common.views import MultiSerializerViewSetMixin, ExportViewSetDataMixin, FSMTransitionActionMixin
from .models import Engagement, AuditorFirm, MicroAssessment, Audit, SpotCheck, PurchaseOrder, \
    AuditorStaffMember, Auditor, AuditPermission
from utils.common.pagination import DynamicPageNumberPagination
from .permissions import HasCreatePermission, CanCreateStaffMembers
from .serializers.auditor import AuditorFirmSerializer, AuditorFirmLightSerializer, PurchaseOrderSerializer, \
    AuditorStaffMemberSerializer, AuditorFirmExportSerializer
from .serializers.engagement import EngagementSerializer, MicroAssessmentSerializer, AuditSerializer, \
    SpotCheckSerializer, EngagementLightSerializer, EngagementExportSerializer
from .metadata import AuditBaseMetadata, EngagementMetadata
from .exports import AuditorFirmCSVRenderer, EngagementCSVRenderer
from .filters import DisplayStatusFilter


class BaseAuditViewSet(
    ExportViewSetDataMixin,
    MultiSerializerViewSetMixin,
):
    metadata_class = AuditBaseMetadata
    pagination_class = DynamicPageNumberPagination
    permission_classes = (IsAuthenticated, )


class AuditorFirmViewSet(
    BaseAuditViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = AuditorFirm.objects.filter(hidden=False)
    serializer_class = AuditorFirmSerializer
    serializer_action_classes = {
        'list': AuditorFirmLightSerializer
    }
    export_serializer_class = AuditorFirmExportSerializer
    renderer_classes = [JSONRenderer, AuditorFirmCSVRenderer]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'email')
    ordering_fields = ('name', )
    filter_fields = ('country', )

    def get_queryset(self):
        queryset = super(AuditorFirmViewSet, self).get_queryset()

        user_type = AuditPermission._get_user_type(self.request.user)
        if not user_type or user_type == Auditor:
            queryset = queryset.filter(staff_members__user=self.request.user)

        return queryset


class PurchaseOrderViewSet(
    BaseAuditViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    @list_route(methods=['get'], url_path='sync/(?P<order_number>[^/]+)')
    def sync(self, request, *args, **kwargs):
        """
        Fetch Purchase Order by vendor number. Load from vision if not found.
        """
        queryset = self.filter_queryset(self.get_queryset())
        instance = queryset.filter(order_number=kwargs.get('order_number')).first()

        if not instance:
            # todo: load from VISION by number
            pass

        if not instance:
            raise Http404

        self.check_object_permissions(self.request, instance)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class EngagementViewSet(
    mixins.CreateModelMixin,
    BaseAuditViewSet,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Engagement.objects.all()
    serializer_class = EngagementSerializer
    serializer_action_classes = {
        'list': EngagementLightSerializer
    }
    metadata_class = EngagementMetadata

    permission_classes = (IsAuthenticated, HasCreatePermission,)
    export_serializer_class = EngagementExportSerializer
    export_filename = 'engagements'
    renderer_classes = [JSONRenderer, EngagementCSVRenderer]

    filter_backends = (SearchFilter, OrderingFilter, DisplayStatusFilter, DjangoFilterBackend)
    search_fields = ('partner__name', 'agreement__order_number', 'agreement__auditor_firm__name')
    ordering_fields = ('agreement__order_number', 'agreement__auditor_firm__name',
                       'partner__name', 'type', 'status')
    filter_fields = ('agreement', 'agreement__auditor_firm', 'partner', 'type')

    def get_serializer_class(self):
        serializer_class = None

        if self.action == 'create':
            engagement_type = self.request.data.get('type', None)

            if engagement_type == Engagement.TYPES.audit:
                serializer_class = AuditSerializer
            elif engagement_type == Engagement.TYPES.ma:
                serializer_class = MicroAssessmentSerializer
            elif engagement_type == Engagement.TYPES.sc:
                serializer_class = SpotCheckSerializer

        return serializer_class or super(EngagementViewSet, self).get_serializer_class()

    def get_queryset(self):
        queryset = super(EngagementViewSet, self).get_queryset()\

        queryset = queryset.prefetch_related(
            'partner', Prefetch('agreement', PurchaseOrder.objects.prefetch_related('auditor_firm'))
        )

        user_type = AuditPermission._get_user_type(self.request.user)
        if not user_type or user_type == Auditor:
            queryset = queryset.filter(staff_members__user=self.request.user)

        return queryset


class EngagementManagementMixin(
    FSMTransitionActionMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    pass


class MicroAssessmentViewSet(EngagementManagementMixin, EngagementViewSet):
    queryset = MicroAssessment.objects.all()
    serializer_class = MicroAssessmentSerializer


class AuditViewSet(EngagementManagementMixin, EngagementViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer


class SpotCheckViewSet(EngagementManagementMixin, EngagementViewSet):
    queryset = SpotCheck.objects.all()
    serializer_class = SpotCheckSerializer


class AuditorStaffMembersViewSet(
    BaseAuditViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AuditorStaffMemberSerializer
    permission_classes = (IsAuthenticated, CanCreateStaffMembers, )
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend, )
    ordering_fields = ('user__email', 'user__first_name', 'id', )
    search_fields = ('user__first_name', 'user__email', 'user__last_name', )

    def get_queryset(self):
        firm_pk = self.kwargs.get('firm_pk')
        return AuditorStaffMember.objects.filter(auditor_firm=firm_pk)

    def perform_create(self, serializer, **kwargs):
        firm_pk = self.kwargs.get('firm_pk')
        instance = serializer.save(auditor_firm_id=firm_pk, **kwargs)
        instance.user.profile.country = self.request.user.profile.country
        instance.user.profile.save()


class EngagementPDFView(SingleObjectMixin, PDFTemplateView):
    template_name = "audit/engagement_pdf.html"
    model = Engagement

    def get_pdf_filename(self):
        return 'engagement_{}.pdf'.format(self.obj.unique_id)

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super(EngagementPDFView, self).dispatch(request, *args, **kwargs)
