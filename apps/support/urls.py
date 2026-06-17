from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.support.views import SupportTicketViewSet

router = DefaultRouter()
router.register('tickets', SupportTicketViewSet, basename='support-tickets')

urlpatterns = [
    path('', include(router.urls)),
]
