from django.urls import path
from django.views.generic import RedirectView
from apps.core.views import (
    PortalLoginView, PortalLogoutView, ClientDashboardView, ClientNewFreightView, ClientTrackingView,
    CarrierDashboardView, OperationsDashboardView, AdminDashboardAPIView, OperationsReportAPIView,
    FinancialReportAPIView, TrackingReportAPIView, AIReportAPIView, AIChatPortalView,
    LandingView, InvestorsView, ProductView, TechnologyView, SecurityView,
    ExecutiveDashboardView, LiveDemoView,
    ExecutiveMetricsAPIView, OperationalMetricsAPIView, FinancialMetricsAPIView, AIMetricsAPIView,
    PublicFreightSimulatorAPIView
)

urlpatterns = [
    # Public Marketing & Product Pages (FreteHub Official Brand Presence)
    path('', LandingView.as_view(), name='landing'),
    path('investors/', InvestorsView.as_view(), name='investors'),
    path('product/', ProductView.as_view(), name='product'),
    path('technology/', TechnologyView.as_view(), name='technology'),
    path('security/', SecurityView.as_view(), name='security'),

    # Redirects for dashboard compatibility
    path('portal/', RedirectView.as_view(pattern_name='client-dashboard', permanent=False)),
    path('carrier/', RedirectView.as_view(pattern_name='carrier-dashboard', permanent=False)),
    path('operations/', RedirectView.as_view(pattern_name='operations-dashboard', permanent=False)),

    # Authentication
    path('portal/login/', PortalLoginView.as_view(), name='portal-login'),
    path('portal/logout/', PortalLogoutView.as_view(), name='portal-logout'),

    # Portals
    path('portal/dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
    path('portal/freights/new/', ClientNewFreightView.as_view(), name='client-new-freight'),
    path('portal/freights/<uuid:pk>/tracking/', ClientTrackingView.as_view(), name='client-tracking'),
    path('portal/ai-chat/', AIChatPortalView.as_view(), name='portal-ai-chat'),
    
    path('carrier/dashboard/', CarrierDashboardView.as_view(), name='carrier-dashboard'),
    
    path('operations/dashboard/', OperationsDashboardView.as_view(), name='operations-dashboard'),
    path('operations/executive-dashboard/', ExecutiveDashboardView.as_view(), name='executive-dashboard'),
    path('demo/live-operation/', LiveDemoView.as_view(), name='live-demo'),

    # Public Rate Limited Freight Simulator
    path('api/public/freight-simulator/', PublicFreightSimulatorAPIView.as_view(), name='api-public-freight-simulator'),

    # Analytics Metrics APIs
    path('api/metrics/executive/', ExecutiveMetricsAPIView.as_view(), name='api-metrics-executive'),
    path('api/metrics/operations/', OperationalMetricsAPIView.as_view(), name='api-metrics-operations'),
    path('api/metrics/financial/', FinancialMetricsAPIView.as_view(), name='api-metrics-financial'),
    path('api/metrics/ai/', AIMetricsAPIView.as_view(), name='api-metrics-ai'),

    # Legacy Reports API endpoints
    path('api/admin/dashboard/', AdminDashboardAPIView.as_view(), name='api-admin-dashboard'),
    path('api/admin/reports/operations/', OperationsReportAPIView.as_view(), name='api-report-operations'),
    path('api/admin/reports/financial/', FinancialReportAPIView.as_view(), name='api-report-financial'),
    path('api/admin/reports/tracking/', TrackingReportAPIView.as_view(), name='api-report-tracking'),
    path('api/admin/reports/ai/', AIReportAPIView.as_view(), name='api-report-ai'),
]
