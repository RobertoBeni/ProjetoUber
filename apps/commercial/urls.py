from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.commercial.views import InvestorLeadViewSet

admin_router = DefaultRouter()
admin_router.register('admin/commercial/leads', InvestorLeadViewSet, basename='admin-commercial-leads')

# Public endpoint (only POST allowed)
public_lead_create = InvestorLeadViewSet.as_view({
    'post': 'create'
})

urlpatterns = [
    path('commercial/leads/', public_lead_create, name='public-commercial-leads-create'),
    path('', include(admin_router.urls)),
]
