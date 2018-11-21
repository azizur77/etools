from datetime import date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _

from rest_framework import mixins, viewsets, views
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unicef_locations.cache import etag_cached
from unicef_locations.models import Location
from unicef_restlib.pagination import DynamicPageNumberPagination
from unicef_restlib.views import SafeTenantViewSetMixin, MultiSerializerViewSetMixin

from etools.applications.field_monitoring.fm_settings.filters import CPOutputIsActiveFilter
from etools.applications.field_monitoring.fm_settings.models import FMMethodType, LocationSite, CPOutputConfig
from etools.applications.field_monitoring.fm_settings.serializers.cp_outputs import FieldMonitoringCPOutputSerializer, \
    CPOutputConfigDetailSerializer
from etools.applications.field_monitoring.fm_settings.serializers.methods import FMMethodSerializer, FMMethodTypeSerializer
from etools.applications.field_monitoring.fm_settings.serializers.sites import LocationSiteSerializer, \
    LocationCountrySerializer
from etools.applications.field_monitoring.shared.models import FMMethod
from etools.applications.permissions2.metadata import BaseMetadata
from etools.applications.reports.models import Result, ResultType


class FMBaseViewSet(
    SafeTenantViewSetMixin,
    MultiSerializerViewSetMixin,
):
    metadata_class = BaseMetadata
    pagination_class = DynamicPageNumberPagination
    permission_classes = [IsAuthenticated, ]


class FMMethodsViewSet(
    FMBaseViewSet,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = FMMethod.objects.all()
    serializer_class = FMMethodSerializer


class FMMethodTypesViewSet(
    FMBaseViewSet,
    viewsets.ModelViewSet
):
    queryset = FMMethodType.objects.all()
    serializer_class = FMMethodTypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = {
        'method': ['exact', 'in'],
    }
    ordering_fields = ('method', 'name',)

    def get_view_name(self):
        return _('Recommended Data Collection Method Types')


class LocationSitesViewSet(
    FMBaseViewSet,
    viewsets.ModelViewSet,
):
    queryset = LocationSite.objects.prefetch_related('parent').order_by('parent__name', 'name')
    serializer_class = LocationSiteSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('is_active',)
    ordering_fields = (
        'parent__gateway__admin_level', 'parent__name',
        'is_active', 'name',
    )
    search_fields = ('parent__name', 'parent__p_code', 'name', 'p_code')

    def get_view_name(self):
        return _('Site Specific Locations')

    @etag_cached('fm-sites')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LocationsCountryView(views.APIView):
    def get(self, request, *args, **kwargs):
        country = get_object_or_404(Location, gateway__admin_level=0)
        return Response(data=LocationCountrySerializer(instance=country).data)


class CPOutputsViewSet(
    FMBaseViewSet,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Result.objects.filter(result_type__name=ResultType.OUTPUT).prefetch_related(
        'fm_config',
        'intervention_links',
        'intervention_links__intervention',
        'intervention_links__intervention__agreement__partner',
    )
    serializer_class = FieldMonitoringCPOutputSerializer
    filter_backends = (DjangoFilterBackend, CPOutputIsActiveFilter, OrderingFilter)
    filter_fields = {
        'fm_config__is_monitored': ['exact'],
        'fm_config__is_priority': ['exact'],
        'parent': ['exact', 'in'],
    }
    ordering_fields = ('name', 'fm_config__is_monitored', 'fm_config__is_priority')

    def get_view_name(self):
        return _('Country Programme Outputs')

    def get_queryset(self):
        queryset = super().get_queryset()

        # return by default everything, including inactive, but not older than 1 year
        return queryset.filter(to_date__gte=date.today() - timedelta(days=365))


class CPOutputConfigsViewSet(
    FMBaseViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = CPOutputConfig.objects.all()
    serializer_class = CPOutputConfigDetailSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('is_monitored', 'is_priority')
    ordering_fields = ('cp_output__name',)
