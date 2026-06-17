from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from apps.freight.models import FreightOrder
from apps.freight.serializers import FreightOrderSerializer
from apps.freight.permissions import IsFreightParticipant
from apps.freight.services import FreightService
from apps.matching.services import MatchingService

class FreightOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the freight order lifecycle, transition events,
    and enforcing secure object access boundaries.
    """
    queryset = FreightOrder.objects.all()
    serializer_class = FreightOrderSerializer
    permission_classes = [IsFreightParticipant]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return FreightOrder.objects.none()
            
        # Object Access Boundary Pattern: return all to allow has_object_permission
        # validation and secure a DRF 403 Forbidden instead of a 404 Not Found.
        if self.action != 'list':
            return FreightOrder.objects.all()

        # Filtering logic for lists
        if user.is_superuser or user.is_staff:
            return FreightOrder.objects.all()
            
        if user.user_type == 'DRIVER':
            # Driver sees assigned freights or those waiting for a driver
            return FreightOrder.objects.filter(
                models.Q(driver=user) | models.Q(status='waiting_driver')
            )
            
        if user.user_type == 'CLIENT':
            # Client sees their own solicited freights
            return FreightOrder.objects.filter(customer=user)
            
        # Carrier Company owner check
        if hasattr(user, 'carrier_company'):
            return FreightOrder.objects.filter(carrier_company=user.carrier_company)
            
        # Driver of a Carrier Company check
        if hasattr(user, 'driver_profile') and user.driver_profile.carrier_company:
            return FreightOrder.objects.filter(carrier_company=user.driver_profile.carrier_company)

        return FreightOrder.objects.filter(customer=user)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        order = self.get_object()
        if order.status != 'waiting_driver':
            return Response(
                {"detail": "Este frete não está aguardando motorista."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            updated_order = FreightService.accept_order(order, request.user)
            serializer = self.get_serializer(updated_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        order = self.get_object()
        from apps.matching.models import MatchCandidate
        MatchCandidate.objects.filter(freight_order=order, driver=request.user, status='pending').update(status='rejected')
        return Response({"detail": "Frete recusado com sucesso."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='arrived-origin')
    def arrived_origin(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['driver_found', 'driver_going_to_pickup']:
            return Response(
                {"detail": "Status inválido para esta ação."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.arrived_origin(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='collect')
    def collect(self, request, pk=None):
        order = self.get_object()
        if order.status != 'arrived_at_origin':
            return Response(
                {"detail": "Status inválido para esta ação. Motorista precisa estar na origem."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.collect_cargo(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='start-transit')
    def start_transit(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['cargo_collected', 'arrived_at_origin']:
            return Response(
                {"detail": "Status inválido para esta ação."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.start_transit(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='arrived-destination')
    def arrived_destination(self, request, pk=None):
        order = self.get_object()
        if order.status != 'in_transit':
            return Response(
                {"detail": "Status inválido para esta ação. Carga precisa estar em trânsito."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.arrived_destination(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['in_transit', 'arrived_at_destination']:
            return Response(
                {"detail": "Status inválido para esta ação."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.deliver_cargo(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.status != 'delivered':
            return Response(
                {"detail": "Status inválido para esta ação. Carga precisa ter sido entregue primeiro."},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_order = FreightService.complete_order(order)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        reason = request.data.get('cancellation_reason', 'Cancelado pelo usuário')
        updated_order = FreightService.cancel_order(order, reason)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='match')
    def run_matching(self, request, pk=None):
        order = self.get_object()
        if order.status != 'waiting_driver':
            return Response(
                {"detail": "Matching só pode ser executado para ordens aguardando motorista."},
                status=status.HTTP_400_BAD_REQUEST
            )
        candidates = MatchingService.find_and_rank_candidates(order)
        from apps.matching.serializers import MatchCandidateSerializer
        serializer = MatchCandidateSerializer(candidates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='route')
    def get_order_route(self, request, pk=None):
        order = self.get_object()
        try:
            route = order.route_details
            from apps.routing.serializers import RouteSerializer
            serializer = RouteSerializer(route)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Rota não encontrada para este frete."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='eta')
    def get_order_eta(self, request, pk=None):
        order = self.get_object()
        eta_record = order.eta_records.first()
        if not eta_record:
            return Response(
                {"detail": "Nenhum registro de ETA encontrado para este frete."},
                status=status.HTTP_404_NOT_FOUND
            )
        from apps.eta.serializers import ETARecordSerializer
        serializer = ETARecordSerializer(eta_record)
        return Response(serializer.data, status=status.HTTP_200_OK)

