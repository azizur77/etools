from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from unicef_locations.cache import etag_cached

from etools.applications.field_monitoring.settings.filters import CPOutputIsActiveFilter
from etools.applications.field_monitoring.settings.models import MethodType, LocationSite, CPOutputConfig
from etools.applications.field_monitoring.settings.serializers.cp_outputs import FieldMonitoringCPOutputSerializer, \
    CPOutputConfigSerializer
from etools.applications.field_monitoring.settings.serializers.locations import LocationSiteSerializer
from etools.applications.field_monitoring.settings.serializers.methods import MethodSerializer, MethodTypeSerializer
from etools.applications.field_monitoring.shared.models import Method
from etools.applications.field_monitoring.views import FMBaseViewSet
from etools.applications.reports.models import Result, ResultType


class MethodsViewSet(
    FMBaseViewSet,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer


class MethodTypesViewSet(
    FMBaseViewSet,
    viewsets.ModelViewSet
):
    queryset = MethodType.objects.all()
    serializer_class = MethodTypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('method',)
    ordering_fields = ('method', 'name',)


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

    @etag_cached('fm-sites')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CPOutputConfigsViewSet(
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
    filter_fields = ('fm_config__is_monitored', 'fm_config__is_priority', 'parent')
    ordering_fields = ('name', 'fm_config__is_monitored', 'fm_config__is_priority')