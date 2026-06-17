from rest_framework import viewsets, permissions
from apps.matching.models import MatchCandidate
from apps.matching.serializers import MatchCandidateSerializer

class MatchCandidateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving and managing matching candidates.
    """
    queryset = MatchCandidate.objects.all()
    serializer_class = MatchCandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MatchCandidate.objects.none()
        if user.is_superuser or user.is_staff:
            return MatchCandidate.objects.all()
        if user.user_type == 'DRIVER':
            return MatchCandidate.objects.filter(driver=user)
        return MatchCandidate.objects.filter(freight_order__customer=user)
