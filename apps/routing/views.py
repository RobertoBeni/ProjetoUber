from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.routing.models import Route
from apps.routing.serializers import RouteSerializer, RouteCalculateInputSerializer
from apps.routing.services import RoutingService

class RouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving simulated route models and calculating route plans.
    """
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        input_serializer = RouteCalculateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        data = input_serializer.validated_data
        
        route_data = RoutingService.calculate_simulated_route(
            origin_lat=data.get('origin_latitude'),
            origin_lng=data.get('origin_longitude'),
            dest_lat=data.get('destination_latitude'),
            dest_lng=data.get('destination_longitude')
        )
        
        return Response(route_data, status=status.HTTP_200_OK)
