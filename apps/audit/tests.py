from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.audit.models import AuditLog

User = get_user_model()

class AuditTests(APITestCase):
    """
    Test suite to verify correct and automated tracking of system AuditLogs.
    Assessing raw responses directly as returned before JSON rendering in DRF testing.
    """
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.user_me_url = reverse('user-me')
        self.audit_log_list_url = reverse('audit-log-list')

        self.payload = {
            "name": "Roberto Silva",
            "email": "roberto@example.com",
            "phone": "(11) 98888-7777",
            "document_type": "CPF",
            "document_number": "123.456.789-01",
            "user_type": "PF",
            "password": "Password123"
        }

    def test_audit_log_created_on_registration_and_login(self):
        """
        Verify AuditLog record is written on user register and login events.
        """
        # 1. Register User
        self.client.post(self.register_url, self.payload, format='json')
        
        # Verify Registration Log exists
        reg_logs = AuditLog.objects.filter(action="Cadastro de Usuário")
        self.assertEqual(reg_logs.count(), 1)
        self.assertEqual(reg_logs.first().user.email, "roberto@example.com")

        # 2. Login User
        login_payload = {
            "email": "roberto@example.com",
            "password": "Password123"
        }
        self.client.post(self.login_url, login_payload, format='json')
        
        # Verify Login Log exists
        login_logs = AuditLog.objects.filter(action="Login com Sucesso")
        self.assertEqual(login_logs.count(), 1)
        self.assertEqual(login_logs.first().user.email, "roberto@example.com")

    def test_audit_logs_restrictions(self):
        """
        Verify that only Admin/Support can access audit log endpoints.
        """
        # Create non-admin
        self.client.post(self.register_url, self.payload, format='json')
        user = User.objects.get(email="roberto@example.com")
        
        # Access logs as PF client (must block)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.audit_log_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Upgrade user to Admin
        user.user_type = "ADMIN"
        user.save()
        
        # Access logs as Admin (must allow)
        response_admin = self.client.get(self.audit_log_list_url)
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
