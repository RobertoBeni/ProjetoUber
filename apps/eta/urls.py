from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.eta.views import ETARecordViewSet

router = DefaultRouter()
router.register(r'eta-records', ETARecordViewSet, basename='eta-record')

urlpatterns = [
    path('', include(router.urls)),
]
