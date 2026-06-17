from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.companies.views import CompanyProfileViewSet, CarrierCompanyViewSet

router = DefaultRouter()
router.register('companies', CompanyProfileViewSet, basename='company')
router.register('carriers', CarrierCompanyViewSet, basename='carrier')

urlpatterns = [
    path('', include(router.urls)),
]
