from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.cargo.models import CargoType
from apps.cargo.serializers import CargoTypeSerializer
from apps.cargo.services import CargoCompatibilityService

class CargoTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for CargoTypes.
    Includes custom vehicle recommendations.
    """
    queryset = CargoType.objects.filter(is_active=True)
    serializer_class = CargoTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='recommend-vehicle')
    def recommend_vehicle(self, request):
        """
        Endpoint: POST /api/cargo/recommend-vehicle/
        Receives cargo details and weight/volume to recommend ideal vehicles.
        """
        cargo_type_slug = request.data.get('cargo_type')
        weight_kg = float(request.data.get('weight_kg', 0))
        volume_m3 = float(request.data.get('volume_m3', 0))
        quantity = int(request.data.get('quantity', 1))
        is_fragile = request.data.get('is_fragile', False)

        if not cargo_type_slug:
            return Response(
                {"detail": "O campo 'cargo_type' (slug) é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recommendation = CargoCompatibilityService.get_recommendation(
            cargo_slug=cargo_type_slug,
            weight_kg=weight_kg,
            volume_m3=volume_m3,
            quantity=quantity,
            is_fragile=is_fragile
        )

        return Response(recommendation, status=status.HTTP_200_OK)
