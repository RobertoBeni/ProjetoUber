from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(APITestCase):
    """
    Test suite for user self-registration, JWT authentication, and profile endpoints.
    Assessing raw responses as returned before JSON rendering in DRF testing.
    """
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('auth-refresh')
        self.logout_url = reverse('auth-logout')
        self.auth_me_url = reverse('auth-me')
        self.user_me_url = reverse('user-me')

        # Test registration payloads
        self.valid_pf_payload = {
            "name": "João Silva",
            "email": "joao@example.com",
            "phone": "(11) 98888-7777",
            "document_type": "CPF",
            "document_number": "123.456.789-01",
            "user_type": "PF",
            "password": "Password123"
        }

    def test_user_self_registration_pf(self):
        """
        Verify that a PF client can register successfully.
        """
        response = self.client.post(self.register_url, self.valid_pf_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # RegisterView explicitly returns {"data": user_data}
        self.assertEqual(response.data['data']['email'], "joao@example.com")
        self.assertEqual(response.data['data']['document_number'], "12345678901")  # Cleaned

    def test_user_self_registration_invalid_cpf(self):
        """
        Verify that registration fails with wrong CPF size.
        """
        payload = self.valid_pf_payload.copy()
        payload['document_number'] = "12345"  # Invalid size
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_jwt_login_flow(self):
        """
        Verify full JWT login, access token usage, refresh, and logout sequence.
        """
        # 1. Register
        self.client.post(self.register_url, self.valid_pf_payload, format='json')

        # 2. Login
        login_payload = {
            "email": "joao@example.com",
            "password": "Password123"
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # JWT Login returns access and refresh at root
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        self.assertIsNotNone(access_token)
        self.assertEqual(response.data['user']['email'], "joao@example.com")

        # 3. Request auth/me using Bearer Access Token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response_me = self.client.get(self.auth_me_url)
        self.assertEqual(response_me.status_code, status.HTTP_200_OK)
        # AuthMeView returns standard serializer data at root
        self.assertEqual(response_me.data['name'], "João Silva")

        # 4. Refresh token (rotates the refresh token!)
        self.client.credentials()  # Clear auth headers
        refresh_payload = {"refresh": refresh_token}
        response_refresh = self.client.post(self.refresh_url, refresh_payload, format='json')
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        
        new_access_token = response_refresh.data['access']
        new_refresh_token = response_refresh.data['refresh']  # Capture rotated refresh token
        self.assertIsNotNone(new_access_token)
        self.assertIsNotNone(new_refresh_token)

        # 5. Logout (uses the rotated, active refresh token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        response_logout = self.client.post(self.logout_url, {"refresh": new_refresh_token}, format='json')
        self.assertEqual(response_logout.status_code, status.HTTP_200_OK)

    def test_profile_update_me(self):
        """
        Verify getting and updating the current user profile.
        """
        # Register and login
        self.client.post(self.register_url, self.valid_pf_payload, format='json')
        login_res = self.client.post(self.login_url, {"email": "joao@example.com", "password": "Password123"}, format='json')
        token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Get profile
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "João Silva")

        # Update profile
        update_payload = {
            "name": "João Silva Alterado",
            "phone": "(11) 91111-2222"
        }
        response_patch = self.client.patch(self.user_me_url, update_payload, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        # UserMeView patch returns {"data": user_data}
        self.assertEqual(response_patch.data['data']['name'], "João Silva Alterado")
        self.assertEqual(response_patch.data['data']['phone'], "(11) 91111-2222")
