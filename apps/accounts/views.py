from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from apps.accounts.serializers import (
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer
)
from apps.audit.services import create_audit_log

User = get_user_model()

class RegisterView(APIView):
    """
    Endpoint: POST /api/auth/register/
    Self-service registration for clients, drivers, and carriers.
    Logs creation event in AuditLog.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            
            # Explicit Audit Log
            create_audit_log(
                user=user,
                action="Cadastro de Usuário",
                entity_type="User",
                entity_id=user.id,
                request=request
            )
            
            return Response(
                {
                    "message": "Cadastro realizado com sucesso.",
                    "data": user_data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint: POST /api/auth/login/
    Custom SimpleJWT login view returning tokens and user info.
    Logs successful login event in AuditLog.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Reconstruct serializer to get access to verified user
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid()
                user = serializer.user
                create_audit_log(
                    user=user,
                    action="Login com Sucesso",
                    entity_type="User",
                    entity_id=user.id,
                    request=request
                )
            except Exception:
                pass
        return response

class LogoutView(APIView):
    """
    Endpoint: POST /api/auth/logout/
    Blacklists the user's refresh token and records audit log.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "O token de atualização ('refresh') é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Explicit Audit Log
            create_audit_log(
                user=request.user,
                action="Logout",
                entity_type="User",
                entity_id=request.user.id,
                request=request
            )
            
            return Response(
                {"message": "Logout realizado com sucesso."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Token inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )

class AuthMeView(APIView):
    """
    Endpoint: GET /api/auth/me/
    Retrieves authenticated user details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserMeView(APIView):
    """
    Endpoints:
    GET /api/users/me/ - Retrieve user profile
    PATCH /api/users/me/ - Update user profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            # Explicit Audit Log for profile changes
            create_audit_log(
                user=user,
                action="Alteração Cadastral",
                entity_type="User",
                entity_id=user.id,
                request=request
            )
            
            return Response(
                {
                    "message": "Perfil atualizado com sucesso.",
                    "data": UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from apps.accounts.models import UserConsent
from apps.accounts.serializers import UserConsentSerializer

class UserConsentViewSet(viewsets.ModelViewSet):
    serializer_class = UserConsentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserConsent.objects.all()
        return UserConsent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR', '')
        
        serializer.save(user=self.request.user, ip_address=ip)

