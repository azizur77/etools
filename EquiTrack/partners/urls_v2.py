from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from partners.views.dashboards import InterventionPartnershipDashView
from partners.views.v1 import PCAPDFView
from partners.views.partner_organization_v2 import (
    PartnerAuthorizedOfficersListAPIVIew,
    PartnerOrganizationAddView,
    PartnerOrganizationAssessmentDeleteView,
    PartnerOrganizationAssessmentListView,
    PartnerOrganizationDeleteView,
    PartnerOrganizationDetailAPIView,
    PartnerOrganizationHactAPIView,
    PartnerOrganizationListAPIView,
    PartnerStaffMemberListAPIVIew,
)
from partners.views.agreements_v2 import (
    AgreementAmendmentListAPIView,
    AgreementListAPIView,
    AgreementDetailAPIView,
    AgreementAmendmentDeleteView,
)
from partners.views.interventions_v2 import (
    InterventionListAPIView,
    InterventionListDashView,
    InterventionDetailAPIView,
    InterventionPlannedVisitsDeleteView,
    InterventionAttachmentDeleteView,
    InterventionResultLinkDeleteView,
    InterventionAmendmentDeleteView,
    InterventionSectorLocationLinkDeleteView,
    InterventionListMapView,
)

from partners.views.v2 import (
    PmpStaticDropdownsListApiView, PMPDropdownsListApiView,
)


# http://www.django-rest-framework.org/api-guide/format-suffixes/

urlpatterns = (

    url(r'^agreements/$', view=AgreementListAPIView.as_view(), name='agreement-list'),
    url(r'^agreements/(?P<pk>\d+)/$', view=AgreementDetailAPIView.as_view(), name='agreement-detail'),
    url(r'^agreements/(?P<agr>\d+)/generate_doc/$', PCAPDFView.as_view(), name='pca_pdf'),
    url(r'^agreements/amendments/$',
        view=AgreementAmendmentListAPIView.as_view(),
        name='agreement-amendment-list'
    ),
    url(r'^agreements/amendments/(?P<pk>\d+)/$',
        view=AgreementAmendmentDeleteView.as_view(http_method_names=['delete']),
        name='agreement-amendment-del'),
    # url(r'^agreements/(?P<pk>\d+)/interventions/$',
    #     view=AgreementInterventionsListAPIView.as_view(),
    #     name='agreement-interventions-list'),

    url(r'^partners/$',
        view=PartnerOrganizationListAPIView.as_view(http_method_names=['get', 'post']),
        name='partner-list'),
    url(r'^partners/hact/$',
        view=PartnerOrganizationHactAPIView.as_view(http_method_names=['get', ]),
        name='partner-hact'),
    url(r'^partners/(?P<pk>\d+)/$',
        view=PartnerOrganizationDetailAPIView.as_view(http_method_names=['get', 'patch']),
        name='partner-detail'),
    url(r'^partners/delete/(?P<pk>\d+)/$',
        view=PartnerOrganizationDeleteView.as_view(http_method_names=['delete']),
        name='partner-delete'),
    url(r'^partners/assessments/$',
        view=PartnerOrganizationAssessmentListView.as_view(http_method_names=['get', ]),
        name='partner-assessment'),
    url(r'^partners/assessments/(?P<pk>\d+)/$',
        view=PartnerOrganizationAssessmentDeleteView.as_view(http_method_names=['delete', ]),
        name='partner-assessment-del'),
    url(r'^partners/add/$', view=PartnerOrganizationAddView.as_view(http_method_names=['post']), name='partner-add'),

    # url(r'^partners/(?P<pk>\d+)/interventions/$',
    #     view=PartnerInterventionListAPIView.as_view(),
    #     name='partner-interventions-list'),
    # url(r'^partners/(?P<partner_pk>\d+)/agreements/$',
    #     view=AgreementListAPIView.as_view(),
    #     name='parter-agreement-list'),
    # url(r'^partners/(?P<partner_pk>\d+)/agreements/(?P<pk>\d+)/interventions/$',
    #     view=AgreementInterventionsListAPIView.as_view(),
    #     name='partner-agreement-interventions-list'),

    url(r'^partners/(?P<partner_pk>\d+)/staff-members/$',
        view=PartnerStaffMemberListAPIVIew.as_view(http_method_names=['get']),
        name='partner-staff-members-list'),
    url(r'^partners/(?P<partner_pk>\d+)/authorized-officers/$',
        view=PartnerAuthorizedOfficersListAPIVIew.as_view(http_method_names=['get']),
        name='partner-authorized-officers-list'),
    # url(r'^staff-members/$', view=PartnerStaffMemberListAPIVIew.as_view(), name='staff-member-list'),
    # url(r'^staff-members/(?P<pk>\d+)/$', view=PartnerStaffMemberDetailAPIView.as_view(), name='staff-member-detail'),
    # url(r'^staff-members/(?P<pk>\d+)/properties/$',
    #     view=PartnerStaffMemberPropertiesAPIView.as_view(),
    # #     name='staff-member-properties'),
    # url(r'^partnership-dash/(?P<ct_pk>\d+)/(?P<office_pk>\d+)/$',
    #     view=PartnershipDashboardAPIView.as_view(),
    #     name='partnership-dash-with-ct-office'),
    # url(r'^partnership-dash/(?P<ct_pk>\d+)/$',
    #     view=PartnershipDashboardAPIView.as_view(),
    #     name='partnership-dash-with-ct'),
    # url(r'^partnership-dash/$', view=PartnershipDashboardAPIView.as_view(), name='partnership-dash'),

    url(r'^interventions/$',
        view=InterventionListAPIView.as_view(http_method_names=['get', 'post']),
        name='intervention-list'),

    url(r'^interventions/dash/$',
        view=InterventionListDashView.as_view(http_method_names=['get', 'post']),
        name='intervention-list-dash'),

    url(r'^interventions/(?P<pk>\d+)/$',
        view=InterventionDetailAPIView.as_view(http_method_names=['get', 'patch']),
        name='intervention-detail'),
    url(r'^interventions/planned-visits/(?P<pk>\d+)/$',
        view=InterventionPlannedVisitsDeleteView.as_view(http_method_names=['delete', ]),
        name='intervention-visits-del'),
    url(r'^interventions/attachments/(?P<pk>\d+)/$',
        view=InterventionAttachmentDeleteView.as_view(http_method_names=['delete', ]),
        name='intervention-attachments-del'),
    url(r'^interventions/results/(?P<pk>\d+)/$',
        view=InterventionResultLinkDeleteView.as_view(http_method_names=['delete', ]),
        name='intervention-results-del'),
    url(r'^interventions/amendments/(?P<pk>\d+)/$',
        view=InterventionAmendmentDeleteView.as_view(http_method_names=['delete', ]),
        name='intervention-amendments-del'),
    url(r'^interventions/sector-locations/(?P<pk>\d+)/$',
        view=InterventionSectorLocationLinkDeleteView.as_view(http_method_names=['delete', ]),
        name='intervention-sector-locations-del'),
    url(r'^interventions/map/$',
        view=InterventionListMapView.as_view(http_method_names=['get', ]),
        name='intervention-map'),
    url(r'^interventions/partnership-dash/$',
        view=InterventionPartnershipDashView.as_view(http_method_names=['get', ]),
        name='interventions-partnership-dash'),

    # TODO: figure this out
    # url(r'^partners/interventions/$', view=InterventionsView.as_view()),
    url(r'^dropdowns/static/$',
        view=PmpStaticDropdownsListApiView.as_view(http_method_names=['get']),
        name='dropdown-static-list'),
    url(r'^dropdowns/pmp/$', view=PMPDropdownsListApiView.as_view(http_method_names=['get']), name='dropdown-pmp-list'),
)
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])
