from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.pricing.views import PriceEstimateViewSet

router = DefaultRouter()
router.register(r'pricing', PriceEstimateViewSet, basename='pricing')

urlpatterns = [
    path('', include(router.urls)),
]
