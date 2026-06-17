from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.freight.views import FreightOrderViewSet
from apps.tracking.views import FreightTrackingDetailAPIView, FreightEventsListAPIView, CreateManualEventAPIView

router = DefaultRouter()
router.register(r'freight-orders', FreightOrderViewSet, basename='freight-order')

urlpatterns = [
    path('freight-orders/<uuid:pk>/tracking/', FreightTrackingDetailAPIView.as_view(), name='freight-tracking-detail'),
    path('freight-orders/<uuid:pk>/events/', FreightEventsListAPIView.as_view(), name='freight-events-list'),
    path('freight-orders/<uuid:pk>/tracking/event/', CreateManualEventAPIView.as_view(), name='freight-create-manual-event'),
    path('', include(router.urls)),
]
