from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleSerializer
from apps.accounts.permissions import IsAdminUserType, IsDriver, IsCarrier
from apps.audit.services import create_audit_log

class IsDriverOrCarrier(permissions.BasePermission):
    """Allows access only to Drivers or Carrier Companies."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.user_type in ['DRIVER', 'CARRIER'])

class IsVehicleOwnerOrStaff(permissions.BasePermission):
    """Allows only the owner (or linked carrier) or support/admin staff to view or modify a vehicle."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.user_type in ['ADMIN', 'SUPPORT']:
            return True
        is_owner = (obj.owner_driver == request.user)
        is_linked_carrier = (obj.carrier_company and obj.carrier_company.owner_user == request.user)
        return is_owner or is_linked_carrier

class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Vehicle records.
    Endpoints:
    - POST /api/vehicles/ (Only DRIVER or CARRIER)
    - GET /api/vehicles/ (Filtered based on ownership / linkages)
    - GET/PATCH /api/vehicles/{id}/
    - POST /api/vehicles/{id}/submit-review/
    - PATCH /api/vehicles/{id}/review/ (Only Admin)
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVehicleOwnerOrStaff]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsDriverOrCarrier()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically assign ownership to the current user
        serializer.save(owner_driver=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit-review')
    def submit_review(self, request, pk=None):
        vehicle = self.get_object()
        
        # Verify ownership boundaries
        is_owner = (vehicle.owner_driver == request.user)
        is_linked_carrier = (vehicle.carrier_company and vehicle.carrier_company.owner_user == request.user)
        
        if not (is_owner or is_linked_carrier or request.user.is_superuser or request.user.user_type == 'ADMIN'):
            return Response(
                {"detail": "Você não tem permissão para submeter este veículo para revisão."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        vehicle.status = 'pending'
        vehicle.save()
        
        create_audit_log(request.user, "Submissão de Veículo para Revisão", "Vehicle", vehicle.id, request)
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                "message": "Veículo submetido para revisão com sucesso.",
                "data": serializer.data
            }
        )

    @action(detail=True, methods=['patch'], url_path='review', permission_classes=[IsAdminUserType])
    def review(self, request, pk=None):
        vehicle = self.get_object()
        status_value = request.data.get('status')
        if status_value not in ['approved', 'rejected', 'suspended']:
            return Response(
                {"detail": "Status de revisão inválido. Opções: approved, rejected, suspended."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        vehicle.status = status_value
        vehicle.save()
        
        # Audit review action
        create_audit_log(request.user, f"Revisão de Veículo: {status_value.upper()}", "Vehicle", vehicle.id, request)
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                "message": f"Status do veículo alterado para {status_value}.",
                "data": serializer.data
            }
        )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.user_type == 'ADMIN':
            return Vehicle.objects.all()
            
        if self.action == 'list':
            if user.user_type == 'DRIVER':
                return Vehicle.objects.filter(owner_driver=user)
                
            if user.user_type == 'CARRIER':
                try:
                    carrier = user.carrier_company
                    # Show vehicles owned by this user or linked to their carrier company
                    return Vehicle.objects.filter(Q(carrier_company=carrier) | Q(owner_driver=user))
                except Exception:
                    return Vehicle.objects.filter(owner_driver=user)
                    
            return Vehicle.objects.filter(owner_driver=user)
            
        return Vehicle.objects.all()
