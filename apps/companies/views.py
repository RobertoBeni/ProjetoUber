from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.companies.models import CompanyProfile, CarrierCompany
from apps.companies.serializers import CompanyProfileSerializer, CarrierCompanySerializer
from apps.accounts.permissions import IsPJClient, IsCarrier, IsAdminUserType

class CompanyProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CompanyProfile.
    Endpoints:
    - POST /api/companies/ (Only PJ Clients)
    - GET /api/companies/me/ (Get own company profile)
    - PATCH /api/companies/{id}/ (Edit own company profile or Admin)
    """
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsPJClient()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically tie the profile to the registering user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            profile = request.user.company_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except CompanyProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil de empresa não encontrado para o usuário atual."},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.user_type == 'ADMIN':
            return CompanyProfile.objects.all()
        return CompanyProfile.objects.filter(user=user)

class CarrierCompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CarrierCompany.
    Endpoints:
    - POST /api/carriers/ (Only Carrier users)
    - GET /api/carriers/me/ (Get own carrier profile)
    - PATCH /api/carriers/{id}/ (Edit own carrier profile or Admin)
    """
    queryset = CarrierCompany.objects.all()
    serializer_class = CarrierCompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsCarrier()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically tie the carrier to the owner user
        serializer.save(owner_user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            carrier = request.user.carrier_company
            serializer = self.get_serializer(carrier)
            return Response(serializer.data)
        except CarrierCompany.DoesNotExist:
            return Response(
                {"detail": "Transportadora não encontrada para o usuário atual."},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.user_type == 'ADMIN':
            return CarrierCompany.objects.all()
        return CarrierCompany.objects.filter(owner_user=user)
