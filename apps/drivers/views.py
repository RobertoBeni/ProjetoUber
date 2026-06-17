import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.drivers.models import DriverProfile
from apps.drivers.serializers import DriverProfileSerializer
from apps.accounts.permissions import IsDriver, IsAdminUserType
from apps.audit.services import create_audit_log

class DriverProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DriverProfile.
    Endpoints:
    - POST /api/drivers/ (Only DRIVER roles)
    - GET/PATCH /api/drivers/me/
    - POST /api/drivers/go-online/
    - POST /api/drivers/go-offline/
    - PATCH /api/drivers/{id}/review/ (Only Admin)
    """
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsDriver()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically bind profile to user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        try:
            profile = request.user.driver_profile
        except DriverProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil de motorista não encontrado para este usuário."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
            
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Perfil de motorista atualizado com sucesso.",
                        "data": serializer.data
                    }
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='go-online')
    def go_online(self, request):
        try:
            profile = request.user.driver_profile
            # Check CNH expiration date
            if profile.cnh_expiration_date < datetime.date.today():
                return Response(
                    {"detail": "Não é possível ficar online com a CNH vencida."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            profile.is_online = True
            profile.save()
            
            # Log the change of driver state
            create_audit_log(request.user, "Motorista Go-Online", "DriverProfile", profile.id, request)
            
            serializer = self.get_serializer(profile)
            return Response(
                {
                    "message": "Motorista está online.",
                    "data": serializer.data
                }
            )
        except DriverProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil de motorista não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='go-offline')
    def go_offline(self, request):
        try:
            profile = request.user.driver_profile
            profile.is_online = False
            profile.save()
            
            create_audit_log(request.user, "Motorista Go-Offline", "DriverProfile", profile.id, request)
            
            serializer = self.get_serializer(profile)
            return Response(
                {
                    "message": "Motorista está offline.",
                    "data": serializer.data
                }
            )
        except DriverProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil de motorista não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'], url_path='review', permission_classes=[IsAdminUserType])
    def review(self, request, pk=None):
        profile = self.get_object()
        status_value = request.data.get('status')
        if status_value not in ['approved', 'rejected', 'suspended']:
            return Response(
                {"detail": "Status de revisão inválido. Opções: approved, rejected, suspended."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        profile.status = status_value
        profile.save()
        
        # Log Administrative review
        create_audit_log(
            request.user, 
            f"Revisão de Motorista: {status_value.upper()}", 
            "DriverProfile", 
            profile.id, 
            request,
            metadata={"driver_user_email": profile.user.email}
        )
        
        serializer = self.get_serializer(profile)
        return Response(
            {
                "message": f"Status do motorista alterado para {status_value}.",
                "data": serializer.data
            }
        )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.user_type == 'ADMIN':
            return DriverProfile.objects.all()
        return DriverProfile.objects.filter(user=user)
