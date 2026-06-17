from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.routing.views import RouteViewSet

router = DefaultRouter()
router.register(r'routing', RouteViewSet, basename='route')

urlpatterns = [
    path('', include(router.urls)),
]
