import tempfile
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.documents.models import Document

User = get_user_model()

class DocumentTests(APITestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            email="doc_owner@fretehub.com",
            password="Password123",
            name="Document Owner",
            phone="(11) 98888-7777",
            document_type="CPF",
            document_number="12345678901",
            user_type="DRIVER",
            is_verified=True
        )
        self.other_user = User.objects.create_user(
            email="doc_other@fretehub.com",
            password="Password123",
            name="Other User",
            phone="(11) 97777-6666",
            document_type="CPF",
            document_number="98765432109",
            user_type="DRIVER",
            is_verified=True
        )
        self.support_user = User.objects.create_user(
            email="support_op@fretehub.com",
            password="Password123",
            name="Support Operator",
            phone="(11) 96666-5555",
            document_type="CPF",
            document_number="11122233344",
            user_type="SUPPORT",
            is_verified=True,
            is_staff=True
        )

        # Login and setup tokens
        response = self.client.post(reverse('auth-login'), {
            "email": "doc_owner@fretehub.com",
            "password": "Password123"
        }, format='json')
        self.owner_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "doc_other@fretehub.com",
            "password": "Password123"
        }, format='json')
        self.other_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "support_op@fretehub.com",
            "password": "Password123"
        }, format='json')
        self.support_token = response.data['access']

        # Setup mock file
        self.test_file = SimpleUploadedFile("cnh.pdf", b"pdf content mock", content_type="application/pdf")

    def test_document_upload_and_ownership(self):
        """Verify uploading a document sets status to pending and binds owner."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        url = reverse('document-list')
        
        payload = {
            "document_type": "CNH",
            "file": SimpleUploadedFile("cnh.pdf", b"pdf content mock", content_type="application/pdf")
        }
        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['owner'], self.owner_user.id)

    def test_document_list_access_boundaries(self):
        """Verify list isolation: normal users see only theirs, support sees all."""
        # 1. Owner uploads a document
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        self.client.post(reverse('document-list'), {"document_type": "CNH", "file": SimpleUploadedFile("cnh.pdf", b"pdf content mock", content_type="application/pdf")}, format='multipart')

        # 2. Other user uploads a document
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        self.client.post(reverse('document-list'), {"document_type": "CRLV", "file": SimpleUploadedFile("crlv.pdf", b"pdf content mock", content_type="application/pdf")}, format='multipart')

        # 3. Other user lists documents - should only see CRLV (1 document)
        list_url = reverse('document-list')
        response = self.client.get(list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['document_type'], 'CRLV')

        # 4. Support operator lists documents - should see both (2 documents)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.support_token}')
        response_support = self.client.get(list_url)
        self.assertEqual(len(response_support.data), 2)

    def test_strictly_protected_access_by_id(self):
        """Verify retrieving document is restricted to owner and staff."""
        # 1. Owner uploads document
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        res = self.client.post(reverse('document-list'), {"document_type": "CNH", "file": SimpleUploadedFile("cnh.pdf", b"pdf content mock", content_type="application/pdf")}, format='multipart')
        document_id = res.data['id']

        # 2. Other user tries to view this document - should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        detail_url = reverse('document-detail', kwargs={'pk': document_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Support user tries to view this document - should succeed
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.support_token}')
        response_support = self.client.get(detail_url)
        self.assertEqual(response_support.status_code, status.HTTP_200_OK)

    def test_document_review_by_support(self):
        """Verify support can approve or reject (rejection reason required)."""
        # 1. Owner uploads
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        res = self.client.post(reverse('document-list'), {"document_type": "CNH", "file": SimpleUploadedFile("cnh.pdf", b"pdf content mock", content_type="application/pdf")}, format='multipart')
        document_id = res.data['id']

        # 2. Try to review as another normal user - should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        review_url = reverse('admin-document-review', kwargs={'pk': document_id})
        response = self.client.patch(review_url, {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Support reviews with rejection without reason - should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.support_token}')
        response = self.client.patch(review_url, {"status": "rejected"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 4. Support reviews with rejection and reason - should succeed
        response = self.client.patch(review_url, {"status": "rejected", "rejection_reason": "Foto ilegível"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'rejected')
        self.assertEqual(response.data['data']['rejection_reason'], 'Foto ilegível')
