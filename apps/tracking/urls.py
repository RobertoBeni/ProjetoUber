from django.urls import path
from apps.tracking.views import TelemetryAPIView

urlpatterns = [
    path('location/', TelemetryAPIView.as_view(), name='tracking-location'),
]
