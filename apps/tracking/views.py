import json
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.freight.models import FreightOrder
from apps.tracking.models import TrackingEvent
from apps.tracking.serializers import TrackingEventSerializer, TelemetryPayloadSerializer
from apps.tracking.services import TrackingService, RedisTrackingClient

class TelemetryAPIView(APIView):
    """
    POST /api/tracking/location/
    Endpoint for continuous real-time telemetry updates submitted by the Driver's mobile client.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Validate if current user is a Driver
        if request.user.user_type != 'DRIVER' and not request.user.is_superuser:
            return Response(
                {"success": False, "message": "Apenas motoristas cadastrados podem enviar telemetria."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TelemetryPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors, "message": "Dados inválidos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        
        try:
            event = TrackingService.process_telemetry(
                freight_order_id=data['freight_order_id'],
                driver_user=request.user,
                latitude=data['latitude'],
                longitude=data['longitude'],
                speed=data.get('speed', 0.00),
                heading=data.get('heading', 0.00),
                timestamp=data.get('timestamp')
            )
            return Response({
                "success": True,
                "data": TrackingEventSerializer(event).data,
                "message": "Localização e telemetria atualizadas com sucesso."
            }, status=status.HTTP_200_OK)
        except PermissionError as pe:
            return Response(
                {"success": False, "message": str(pe)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValueError as ve:
            return Response(
                {"success": False, "message": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "Erro ao processar telemetria."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FreightTrackingDetailAPIView(APIView):
    """
    GET /api/freight-orders/{id}/tracking/
    Retrieves the current real-time telemetric position of the shipment from Redis cache.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        freight_order = get_object_or_404(FreightOrder, id=pk)
        
        # Verify access permission
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            if freight_order.customer != request.user and freight_order.driver != request.user:
                # Check transport company mapping
                if freight_order.carrier_company and freight_order.carrier_company.owner_user != request.user:
                    return Response(
                        {"success": False, "message": "Sem permissão para visualizar o rastreamento deste frete."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                elif not freight_order.carrier_company:
                    return Response(
                        {"success": False, "message": "Sem permissão para visualizar o rastreamento deste frete."},
                        status=status.HTTP_403_FORBIDDEN
                    )

        r = RedisTrackingClient.get_client()
        cached_data = r.get(f"tracking:order:{freight_order.id}:current_location")
        
        if cached_data:
            data = json.loads(cached_data)
        else:
            # Fallback to model coordinate fields
            data = {
                'latitude': str(freight_order.driver.driver_profile.current_latitude) if freight_order.driver and freight_order.driver.driver_profile.current_latitude else str(freight_order.origin_latitude),
                'longitude': str(freight_order.driver.driver_profile.current_longitude) if freight_order.driver and freight_order.driver.driver_profile.current_longitude else str(freight_order.origin_longitude),
                'speed': "0.00",
                'heading': "0.00",
                'timestamp': freight_order.updated_at.isoformat(),
                'freight_order_id': str(freight_order.id),
                'driver_id': str(freight_order.driver.id) if freight_order.driver else "",
                'vehicle_id': str(freight_order.vehicle.id) if freight_order.vehicle else ""
            }

        return Response({
            "success": True,
            "data": data,
            "message": "Localização atual obtida com sucesso."
        }, status=status.HTTP_200_OK)

class FreightEventsListAPIView(APIView):
    """
    GET /api/freight-orders/{id}/events/
    Lists all TrackingEvent history records related to the specific FreightOrder.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        freight_order = get_object_or_404(FreightOrder, id=pk)
        
        # Verify access permission
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            if freight_order.customer != request.user and freight_order.driver != request.user:
                if freight_order.carrier_company and freight_order.carrier_company.owner_user != request.user:
                    return Response(
                        {"success": False, "message": "Sem permissão para visualizar os eventos deste frete."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                elif not freight_order.carrier_company:
                    return Response(
                        {"success": False, "message": "Sem permissão para visualizar os eventos deste frete."},
                        status=status.HTTP_403_FORBIDDEN
                    )

        events = TrackingEvent.objects.filter(freight_order=freight_order).order_by('created_at')
        serializer = TrackingEventSerializer(events, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "Eventos de rastreamento obtidos com sucesso."
        }, status=status.HTTP_200_OK)

class CreateManualEventAPIView(APIView):
    """
    POST /api/freight-orders/{id}/tracking/event/
    Allows drivers or operators to manually submit a logistical event (e.g. logging delay, uploading photo).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        freight_order = get_object_or_404(FreightOrder, id=pk)
        
        # Verify driver or operational team
        is_assigned_driver = (freight_order.driver == request.user)
        is_admin_operator = request.user.is_superuser or request.user.user_type in ['ADMIN', 'SUPPORT', 'LOGISTICS']
        
        if not is_assigned_driver and not is_admin_operator:
            return Response(
                {"success": False, "message": "Sem permissão para registrar eventos manuais neste frete."},
                status=status.HTTP_403_FORBIDDEN
            )

        event_type = request.data.get('event_type', 'occurrence_registered')
        description = request.data.get('description', '')
        
        lat_val = request.data.get('latitude')
        lng_val = request.data.get('longitude')
        
        # Default coordinates to active driver coords if omitted
        if lat_val is None or lng_val is None:
            if freight_order.driver and hasattr(freight_order.driver, 'driver_profile'):
                lat_val = freight_order.driver.driver_profile.current_latitude or freight_order.origin_latitude
                lng_val = freight_order.driver.driver_profile.current_longitude or freight_order.origin_longitude
            else:
                lat_val = freight_order.origin_latitude
                lng_val = freight_order.origin_longitude

        event = TrackingEvent.objects.create(
            freight_order=freight_order,
            driver=freight_order.driver,
            vehicle=freight_order.vehicle,
            event_type=event_type,
            latitude=Decimal(str(lat_val)) if lat_val else None,
            longitude=Decimal(str(lng_val)) if lng_val else None,
            description=description,
            image=request.FILES.get('image'),
            signature=request.FILES.get('signature'),
            previous_status=freight_order.status,
            new_status=freight_order.status,
            created_by=request.user
        )

        return Response({
            "success": True,
            "data": TrackingEventSerializer(event).data,
            "message": "Evento registrado manualmente com sucesso."
        }, status=status.HTTP_201_CREATED)
