from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.drivers.views import DriverProfileViewSet

router = DefaultRouter()
router.register('drivers', DriverProfileViewSet, basename='driver')

# Secondary mapping to exactly match the requested administrative path: /api/admin/drivers/{id}/review/
admin_review_action = DriverProfileViewSet.as_view({'patch': 'review'})

urlpatterns = [
    path('', include(router.urls)),
    path('admin/drivers/<uuid:pk>/review/', admin_review_action, name='admin-driver-review'),
]
