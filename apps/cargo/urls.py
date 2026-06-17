from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cargo.views import CargoTypeViewSet

router = DefaultRouter()
router.register('', CargoTypeViewSet, basename='cargo-type')

urlpatterns = [
    path('', include(router.urls)),
]

