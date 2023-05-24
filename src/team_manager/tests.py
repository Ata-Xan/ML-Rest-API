import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import  AccessToken, RefreshToken
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail
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





































# class BaseTestCase(APITestCase):
#     def setUp(self):
#         self.user_data = {
#             'email': 'test@example.com',
#             'password': 'testpassword',
#         }
#         self.user = User.objects.create_user(**self.user_data)

#         self.register_url = reverse('user-list')
#         self.login_url = reverse('token_login')
#         self.logout_url = reverse('token_logout')

#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token()}')

#     def get_token(self):
#         response = self.client.post(self.login_url, self.user_data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         return response.data['access']

# class LoginTestCase(BaseTestCase):
#     def test_valid_login(self):
#         response = self.client.post(self.login_url, self.user_data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access', response.data)
#         self.assertIn('refresh', response.data)

#     def test_invalid_login(self):
#         invalid_data = {
#             'email': 'test@example.com',
#             'password': 'wrongpassword',
#         }
#         response = self.client.post(self.login_url, invalid_data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    # def test_registration_duplicate_username(self):
    #     # Make a POST request to register a user with an existing username
    #     response = self.client.post("/api/register/", self.user_data, format="json")

    #     # Assert that the registration fails due to duplicate username (status code 400)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# class LoginTestCase(CoreTestCase):
#     def test_login_success(self):
#         # Make a POST request to login with valid credentials
#         response = self.client.post("/api/login/", self.user_data, format="json")

#         # Assert that the login was successful (status code 200)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_login_invalid_credentials(self):
#         # Make a POST request to login with invalid credentials
#         invalid_user_data = {
#             "username": "testuser",
#             "password": "wrongpassword",
#         }
#         response = self.client.post("/api/login/", invalid_user_data, format="json")

#         # Assert that the login fails due to invalid credentials (status code 401)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# class LogoutTestCase(CoreTestCase):
#     def test_logout_success(self):
#         # Make a POST request to logout with the refresh token
#         headers = {"Authorization": self.auth_header}
#         data = {"refresh": self.refresh_token}
#         response = self.client.post("/api/logout/", data, headers=headers, format="json")

#         # Assert that the logout was successful (status code 205)
#         self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)



























# User = get_user_model()
#  TODO:define a core classs with some user, teams and memberships and then inherit this in the following 
# # test classes:

# # differences between "setUp" and "setUpTestData" => use setUpTestData
# class UserRegistrationTestCase(APITestCase):
#     def test_user_registration(self):
#         url = reverse('user-register')
#         data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'password': 'testpassword',
#         }
#         # username unique
#         # email unique
#         # password confirmation
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue('refresh' in response.data)
#         self.assertTrue('access' in response.data)
# class UserLoginTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='testuser@example.com',
#             password='testpassword',
#         )

#     def test_user_login(self):
#         url = reverse('user-login')
#         data = {
#             'username': 'testuser',
#             'password': 'testpassword',
#         }

#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue('refresh' in response.data)
#         self.assertTrue('access' in response.data)

#     def test_invalid_user_login(self):
#         url = reverse('user-login')
#         data = {
#             'username': 'testuser',
#             'password': 'wrongpassword',
#         }

#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# class LogoutViewSetTest(APITestCase):
#     def setUp(self):
#         # Create a user
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#     # do not use forceauthentication
#     def test_user_logout(self):
#         # Log in the user to authenticate the request
#         self.client.force_authenticate(user=self.user)
#         # Obtain JWT access and refresh tokens
#         token = RefreshToken.for_user(self.user)
#         # Provide the refresh token in the request data
#         data = {'refresh_token': str(token)}
#         # Make a POST request to the logout endpoint
#         response = self.client.post(reverse('user-logout'), data, format='json')
#         # Assert that the response has a 204 NO CONTENT status code
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         # Assert that the refresh token is blacklisted
#         self.assertTrue(RefreshToken(token).blacklisted)

#     def test_user_logout_without_token(self):
#         # Log in the user to authenticate the request
#         self.client.force_authenticate(user=self.user)
#         # Make a POST request to the logout endpoint without providing a refresh token
#         response = self.client.post(reverse('user-logout'), format='json')
#         # Assert that the response has a 400 BAD REQUEST status code
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



# class UserLogoutTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#         username='testuser',
#         email='testuser@example.com',
#         password='testpassword',
#     )
#         refresh = RefreshToken.for_user(self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
#         self.access_token = str(refresh.access_token)
#         self.refresh_token = str(refresh)

#     def test_user_logout(self):
#         url = reverse('user-logout')

#         response = self.client.post(
#             url,
#             {'refresh_token': self.refresh_token},
#             format='json',
#             HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
#         )
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_user_logout_without_token(self):
#         url = reverse('user-logout')

#         # No token provided in the request

#         response = self.client.post(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

















# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from rest_framework.test import APITestCase
# from rest_framework.test import APIClient
# from team_manager.serializers import  TeamSerializer
# from .models import Membership, Team, User

# User = get_user_model()

# class AuthenticationTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')

#         self.client.force_authenticate(user=self.user)
#                 # Create some sample teams 
#         self.team1 = Team.objects.create(name='Team 1')
#         self.team2 = Team.objects.create(name='Team 2')
#         self.team3 = Team.objects.create(name='Team 3')

#          # Create some sample users
#         self.user1 = User.objects.create_user(username='user1', password='pass1')
#         self.user2 = User.objects.create_user(username='user2', password='pass2')
#         self.user3 = User.objects.create_user(username='user3', password='pass3')


#         self.membership1 = Membership.objects.create(user=self.user, team=self.team1, role='Manager')
#         self.membership2 = Membership.objects.create(user=self.user, team=self.team2, role='Viewer')

#     def test_login(self):
#         url = reverse('login')
#         data = {'username': 'testuser', 'password': 'testpassword'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('token', response.data)

#     def test_logout(self):
#         url = reverse('logout')
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_register(self):
#         url = reverse('register')
#         data = {'username': 'newuser', 'password': 'newpassword'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn('token', response.data)

#         # Additional assertion to verify the new user in the database
#         user = User.objects.get(username='newuser')
#         self.assertIsNotNone(user)

# class UserTestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')

#     def test_user_by_authenticated_user(self):
#         url = '/api/user/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)
    
#     def test_user_by_non_authenticated_user(self):
#         self.client.logout()
#         url = '/api/user/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
        
# class MembershipFilterTestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')
        
#         # Create some test teams
#         self.team1 = Team.objects.create(name='Team 1')
#         self.team2 = Team.objects.create(name='Team 2')
#         self.team3 = Team.objects.create(name='Team 3')
#         self.team4 = Team.objects.create(name='Team 4')

#         self.membership1 = Membership.objects.create(user=self.user1, team=self.team1, role='Manager')
#         self.membership2 = Membership.objects.create(user=self.user, team=self.team1, role='Viewer')
#         self.membership3 = Membership.objects.create(user=self.user, team=self.team3, role='Manager')
#         self.membership4 = Membership.objects.create(user=self.user, team=self.team4, role='Viewer')

#     def test_membership_by_authenticated_user(self):
#         url = '/api/memberships/'
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 3)


#     def test_membership_by_non_authenticated_user(self):
#         self.client.logout()
#         url = '/api/teams/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_membership_by_non_existent_user_id(self):
#         response = self.client.get('/membership/?user=123')
#         self.assertEqual(response.status_code, 404)

# class TeamViewSetTestCase(APITestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')
        
#         # Create some test teams
#         self.team1 = Team.objects.create(name='Team 1')
#         self.team2 = Team.objects.create(name='Team 2')
#         self.team3 = Team.objects.create(name='Team 3')
#         self.team4 = Team.objects.create(name='Team 4')
        
#         # Assign memberships to teams
#         self.team1.membership_set.create(user=self.user, role='Manager', team=self.team1)
#         self.team2.membership_set.create(user=self.user, role='Viewer', team=self.team2)
#         self.team2.membership_set.create(user=self.user, role='Viewer', team=self.team4)

#     def test_teams_by_authenticated_user(self):
#         # Ensure authenticated user can list teams
#         url = '/api/teams/'
#         response = self.client.get(url)
#         teams = Team.objects.filter(membership__user=self.user)
#         serializer = TeamSerializer(teams, many=True)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, serializer.data)
    
#     def test_teams_by_nonauthenticated_user(self):
#         # Ensure unauthenticated user cannot list teams
#         self.client.logout()
#         url = '/api/teams/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)