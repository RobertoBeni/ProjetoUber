from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.commercial.models import InvestorLead
from apps.audit.models import AuditLog

User = get_user_model()

class LeadAPITests(APITestCase):
    def setUp(self):
        # Create different kinds of users
        self.public_client = self.client
        
        self.normal_user = User.objects.create_user(
            email="client_pf@fretehub.com",
            password="ClientPassword123",
            name="Roberto Cliente",
            user_type="PF"
        )
        
        self.staff_admin = User.objects.create_user(
            email="admin_commercial@fretehub.com",
            password="AdminPassword123",
            name="Admin Comercial",
            user_type="ADMIN"
        )
        
        self.staff_support = User.objects.create_user(
            email="support_commercial@fretehub.com",
            password="SupportPassword123",
            name="Suporte Comercial",
            user_type="SUPPORT"
        )
        
        self.lead_payload = {
            "name": "Alexandre Pires",
            "email": "alexandre@piresinvest.com",
            "phone": "(11) 98888-5555",
            "company": "Pires Investments",
            "profile_type": "investor",
            "message": "Tenho grande interesse na rodada Seed de R$ 2M."
        }

    def test_public_can_create_lead(self):
        url = reverse('public-commercial-leads-create')
        response = self.client.post(url, self.lead_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InvestorLead.objects.count(), 1)
        
        lead = InvestorLead.objects.first()
        self.assertEqual(lead.name, "Alexandre Pires")
        self.assertEqual(lead.email, "alexandre@piresinvest.com")
        self.assertEqual(lead.status, "new")
        
        # Verify Audit Log
        audit = AuditLog.objects.filter(entity_type="InvestorLead", entity_id=str(lead.id)).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, "CREATE_LEAD")

    def test_public_cannot_list_leads(self):
        url = reverse('admin-commercial-leads-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_user_cannot_list_leads(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('admin-commercial-leads-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_and_update_leads(self):
        # Create a lead first
        lead = InvestorLead.objects.create(
            name="Investimentos S/A",
            email="invest@sa.com",
            profile_type="investor"
        )
        
        # Authenticate as commercial staff
        self.client.force_authenticate(user=self.staff_admin)
        
        # List
        url_list = reverse('admin-commercial-leads-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)
        
        # Partial Update (PATCH)
        url_detail = reverse('admin-commercial-leads-detail', kwargs={'pk': lead.id})
        patch_payload = {
            "status": "contacted",
            "notes": "Primeiro contato telefônico realizado."
        }
        
        response_patch = self.client.patch(url_detail, patch_payload, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        
        lead.refresh_from_db()
        self.assertEqual(lead.status, "contacted")
        self.assertEqual(lead.notes, "Primeiro contato telefônico realizado.")
        
        # Verify Audit Log for update
        audit = AuditLog.objects.filter(action="UPDATE_LEAD", entity_id=str(lead.id)).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.user, self.staff_admin)
