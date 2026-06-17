from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.vehicles.views import VehicleViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet, basename='vehicle')

# Secondary mapping to exactly match the requested administrative path: /api/admin/vehicles/{id}/review/
admin_review_action = VehicleViewSet.as_view({'patch': 'review'})

urlpatterns = [
    path('', include(router.urls)),
    path('admin/vehicles/<uuid:pk>/review/', admin_review_action, name='admin-vehicle-review'),
]
