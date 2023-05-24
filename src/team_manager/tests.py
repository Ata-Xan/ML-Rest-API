import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import  AccessToken, RefreshToken
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User


class CoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_admin = {
            'email': 'test@example.com',
            'password': 'password123',
        }
        self.user = User.objects.create_user(**self.user_admin)
        self.login_url = reverse('login-list')
        self.logout_url = reverse('logout-list')
        self.register_url = reverse('register-list')


class RegistrationTestCase(CoreTestCase):
    def test_registration(self):
        
        new_user = {
            'email': 'test2@example.com',
            'password': 'password123',
        }
        response = self.client.post(self.register_url, new_user ,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_registration_with_existing_email(self):
        # User.objects.create(email="test@example.com", password="password123")
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.client.post(self.register_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
class LoginTestCase(CoreTestCase):
    def test_login(self):
        response = self.client.post(self.login_url, self.user_admin, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
         # Decode the access token
        access_token_obj = AccessToken(token=access_token)
        user_id = access_token_obj['user_id']

        # Ensure the access token is valid for the user
        self.assertEqual(user_id, self.user.id)
    
    def test_register_login(self):
        # register a user
        new_user = {
            'email': 'test2@example.com',
            'password': 'password123',
        }
        
        response = self.client.post(self.register_url, new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)


        # Get the created user from the database
        registered_user = User.objects.get(email=new_user['email'])
        # print(registered_user)
        # Assert that the user exists in the database
        self.assertIsNotNone(registered_user)
        
        # Assert that the user's password is correctly stored
        self.assertTrue(registered_user.check_password(new_user['password']))

        #login with the registered user

        response = self.client.post(self.login_url, new_user, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    
    def test_login_with_invalid_credentials(self):
        credentials = {
            'email': 'invalid_email@example.com',
            'password': 'invalid_password',
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Invalid credentials')
    def test_login_with_missing_email_field(self):
       
        credentials = {
            'password': self.user_admin['password'],
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email is not provided', response.data['detail'])
    def test_login_with_missing_email_field(self):
       
        credentials = {
            'email': self.user_admin['email'],
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password is not provided', response.data['detail'])

    def test_login_twice_with_same_credentials(self):
    
        response = self.client.post(self.login_url, self.user_admin, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

        # Get the JWT token from the response
        jwt_token = response.data['access']

        # Immediately after logging in, try to login again with the same credentials.
        # Include the JWT token in the Authorization header of the request
        response = self.client.post(
            self.login_url,
            self.user_admin,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {jwt_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'You are already logged in')

class LogoutTestCase(CoreTestCase):
    def test_logout(self):
        

        login_response = self.client.post(self.login_url, self.user_admin, format='json')
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Refresh the access token before logout
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)