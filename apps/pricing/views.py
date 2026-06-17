from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.pricing.models import PriceEstimate
from apps.pricing.serializers import PriceEstimateSerializer, PriceEstimateInputSerializer
from apps.pricing.services import PricingService

class PriceEstimateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving price estimate histories and calculating dynamic tariffs.
    """
    queryset = PriceEstimate.objects.all()
    serializer_class = PriceEstimateSerializer

    def get_queryset(self):
        # Clients see only their price estimate history, Admins see all
        user = self.request.user
        if not user.is_authenticated:
            return PriceEstimate.objects.none()
        if user.is_superuser or user.is_staff:
            return PriceEstimate.objects.all()
        return PriceEstimate.objects.filter(customer=user)

    @action(detail=False, methods=['post'], url_path='estimate')
    def estimate(self, request):
        input_serializer = PriceEstimateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        data = input_serializer.validated_data
        
        estimate = PricingService.calculate_estimate(
            customer=request.user,
            origin_lat=data.get('origin_latitude'),
            origin_lng=data.get('origin_longitude'),
            dest_lat=data.get('destination_latitude'),
            dest_lng=data.get('destination_longitude'),
            cargo_type_slug=data.get('cargo_type_slug'),
            requires_helper=data.get('requires_helper', False),
            requires_insurance=data.get('requires_insurance', False)
        )
        
        serializer = self.get_serializer(estimate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
