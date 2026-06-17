from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.matching.views import MatchCandidateViewSet

router = DefaultRouter()
router.register(r'match-candidates', MatchCandidateViewSet, basename='match-candidate')

urlpatterns = [
    path('', include(router.urls)),
]
