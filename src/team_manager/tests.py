import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import  AccessToken, RefreshToken

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from team_manager.serializers import TeamSerializer

from .models import Membership, Team, User
User = get_user_model()

class CoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_admin = {
            'email': 'test@example.com',
            'password': 'password123',
        }
        self.user_client1 = {
            'email':'client@example.com',
            'password':'password',
        }
        self.user_client2 = {
            'email': 'client1@example.com',
            'password': 'password1',
        }
        self.user_client3 = {
            'email':'client2@example.com',
            'password':'password2',
        }

        self.user_aunathenticated = {
            'email':'unauthenticated@user.com',
            'password':'password2',
        }

        self.team_sample={
            'name':'sample'
        }

        self.client1 = User.objects.create_user(**self.user_client1)
        self.client2 = User.objects.create_user(**self.user_client2)
        self.client3 = User.objects.create_user(**self.user_client3)
        self.admin_user = User.objects.create_user(**self.user_admin)

        self.team1 = Team.objects.create(name='Team 1')
        self.team2 = Team.objects.create(name='Team 2')
        self.team3 = Team.objects.create(name='Team 3')
        self.team4 = Team.objects.create(name='Team 4')

        self.membership1 = Membership.objects.create(user=self.admin_user, team=self.team1, role='Manager')
        self.membership2 = Membership.objects.create(user=self.client1, team=self.team1, role='Viewer')
        self.membership3 = Membership.objects.create(user=self.client1, team=self.team3, role='Manager')
        self.membership4 = Membership.objects.create(user=self.admin_user, team=self.team4, role='Viewer')

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
        self.assertEqual(User.objects.count(), 5)

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
        self.assertEqual(user_id, self.admin_user.id)
    
    def test_register_login(self):
        # register a user
        new_user = {
            'email': 'test2@example.com',
            'password': 'password123',
        }
        
        response = self.client.post(self.register_url, new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 5)


        # Get the created user from the database
        registered_user = User.objects.get(email=new_user['email'])
        
        # Assert that the user exists in the database
        self.assertIsNotNone(registered_user)
        
        # Assert that the user's password is correctly stored
        self.assertTrue(registered_user.check_password(new_user['password']))

        #login with the registered user

        response = self.client.post(self.login_url, new_user, format='json')
      
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

class UserTestCase(CoreTestCase):
   
    def test_user_by_authenticated_user(self):
        login_response = self.client.post(self.login_url, self.user_client1, format='json')
        
        refresh_token = login_response.data['refresh']
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        url = '/api/user/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_user_by_non_authenticated_user(self):
        # self.client.logout()
        url = '/api/user/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multiple_users(self):
        # First user login
        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)

        client2 = APIClient()  # Create a separate client instance for the second user
        login_response2 = client2.post(self.login_url, self.user_client2, format='json')
        self.assertEqual(login_response2.status_code, 200)  # Ensure successful login

        refresh_token2 = login_response2.data['refresh']
        refresh2 = RefreshToken(refresh_token2)
        new_access_token2 = str(refresh2.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        client2.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token2}')

        url = '/api/user/'
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 1)

        response2 = client2.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.data), 1)

class TeamViewSetTestCase(CoreTestCase):

    def test_teams_by_authenticated_user(self):
        # Ensure authenticated user can list teams
        
        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        
        url = reverse('team-list')
        # url = '/api/user/'
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)

    
    def test_teams_by_nonauthenticated_user(self):
        # Ensure unauthenticated user cannot list teams
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_update_team_name_with_manager_user(self):
        team_detail_url = reverse('team-detail', args=[self.team3.id])  # Replace with the appropriate URL for your team endpoint
        url = reverse('membership-detail', args=[self.membership1.id])

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        name_before_update = self.team3.name
        # Make a PUT request to update the team
        data = {'name': 'Updated Team Name'}
        response = self.client.put(team_detail_url, data, format='json')
        
        # Assert that the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh the team from the database
        self.team3.refresh_from_db()
        name_after_update = self.team3.name
        # Assert that the team's name has been updated
        self.assertEqual(self.team3.name, name_after_update)

    def test_update_team_name_with_viewer_user(self):
        team_detail_url = reverse('team-detail', args=[self.team1.id])  # Replace with the appropriate URL for your team endpoint

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        
        # Make a PUT request to update the team
        name_before_update = self.team3.name
        data = {'name': 'Updated Team Name'}
        response = self.client.put(team_detail_url, data, format='json')
        
        # Assert that the request was successful (status code 403)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Refresh the team from the database
        self.team3.refresh_from_db()
        
        # Assert that the team's name has been updated
        self.assertEqual(self.team3.name, name_before_update)
    
    def test_delete_team_name_with_manager_user(self):
        team_detail_url = reverse('team-detail', args=[self.team3.id])  # Replace with the appropriate URL for your team endpoint

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        name_before_update = self.team3.name
        number_of_teams_before_deletion = Team.objects.count()

        response = self.client.delete(team_detail_url, format='json')

        # self.team3.refresh_from_db()
        number_of_teams_after_deletion = Team.objects.count()
        # print("number of teams after deletion:",Team.objects.count())


        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(number_of_teams_before_deletion, number_of_teams_after_deletion+1)
    
    def test_delete_team_name_with_viewer_user(self):
        team_detail_url = reverse('team-detail', args=[self.team1.id])  # Replace with the appropriate URL for your team endpoint

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        number_of_teams_before_deletion = Team.objects.count()
        response = self.client.delete(team_detail_url, format='json')
        number_of_teams_after_deletion = Team.objects.count()

        print(response.content)
        
        self.assertEqual(number_of_teams_before_deletion, number_of_teams_after_deletion)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_team_with_authenticated_user(self):
        team_list_url = reverse('team-list')  # Replace 'team-list' with your actual URL name for team list

        login_response = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token = login_response.data['refresh']
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')

        # Make a POST request to create a team
        data = {'name': 'New Team'}

        number_of_teams_before_creation = Team.objects.count()
        response = self.client.post(team_list_url, data, format='json')
        number_of_teams_after_creation = Team.objects.count()
        # Assert the response and perform further assertions as needed
        self.assertEqual(number_of_teams_before_creation, number_of_teams_after_creation-1)

        self.assertEqual(response.status_code, 201)  # 201 represents successful creation

        # Retrieve the newly created team from the response data
        team_id = response.data['id']
        created_team = Team.objects.get(id=team_id)

        # Assert that the team name is correct
        self.assertEqual(created_team.name, 'New Team')

    def test_create_team_with_unauthenticated_user(self):
        team_list_url = reverse('team-list')  # Replace 'team-list' with your actual URL name for team list

        login_response = self.client.post(self.login_url, self.user_aunathenticated, format='json')
        

        data = {'name': 'New Team'}

        number_of_teams_before_creation = Team.objects.count()
        response = self.client.post(team_list_url, data, format='json')
        number_of_teams_after_creation = Team.objects.count()
        # Assert the response and perform further assertions as needed
        self.assertEqual(number_of_teams_before_creation, number_of_teams_after_creation)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # 201 represents successful creation

class MembershipFilterTestCase(CoreTestCase):


    def test_membership_by_authenticated_user(self):
        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        
        url = reverse('membership-list')

        # url = '/api/user/'
        response1 = self.client.get(url)
        # print("membership: ", response1.content)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)

    def test_memberships_by_nonauthenticated_user(self):
        # Ensure unauthenticated user cannot list teams
        url = reverse('membership-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_membership_with_manager_user(self):

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')

        membership_detail_url = reverse('membership-detail', args=[self.membership3.pk])  # Replace with the appropriate URL for your team endpoint
        update_data = {
            'role': 'Viewer',
            'user': self.membership3.user.pk,  # Include the user field
            'team': self.membership3.team.pk,  # Include the team field
        }
        
        # Make a PUT request to update the team
        response = self.client.put(membership_detail_url, update_data, format='json')
        print("membership update:", response.content)
        # Assert that the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh the team from the database
        self.membership3.refresh_from_db()
        role_after_update = self.membership3.role
        # Assert that the team's name has been updated
        self.assertEqual(self.membership3.role, role_after_update)

    def test_update_membership_with_viewer_user(self):

        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)

        update_data = {
            'role': 'Viewer',
            'user': self.membership3.user.pk,  # Include the user field
            'team': self.membership3.team.pk,  # Include the team field
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        membership_detail_url = reverse('membership-detail', args=[self.membership1.pk])  # Replace with the appropriate URL for your team endpoint

        # Make a PUT request to update the team
        name_before_update = self.membership1.role
        response = self.client.put(membership_detail_url, update_data, format='json')
        
        # Assert that the request was successful (status code 403)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Refresh the team from the database
        self.team3.refresh_from_db()
        
        # Assert that the team's name has been updated
        self.assertEqual(self.membership1.role, name_before_update)
    
    def test_delete_membership_with_manager_user(self):

        login_response1 = self.client.post(self.login_url, self.user_admin, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        number_of_memberships_before_deletion = Membership.objects.count()

        membership_detail_url = reverse('membership-detail', args=[self.membership1.pk])  # Replace with the appropriate URL for your team endpoint


        response = self.client.delete(membership_detail_url,format='json')
        print("deleteion response.content: ",response.content)
        # self.membership3.refresh_from_db()
        number_of_memberships_after_deletion = Membership.objects.count()
        # print("number of teams after deletion:",Team.objects.count())


        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(number_of_memberships_before_deletion, number_of_memberships_after_deletion+1)
    
    def test_delete_membership_with_viewer_user(self):
        login_response1 = self.client.post(self.login_url, self.user_client1, format='json')
        refresh_token1 = login_response1.data['refresh']
        refresh1 = RefreshToken(refresh_token1)
        new_access_token1 = str(refresh1.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token1}')
        number_of_memberships_before_deletion = Membership.objects.count()

        membership_detail_url = reverse('membership-detail', args=[self.membership2.pk])  # Replace with the appropriate URL for your team endpoint
        update_data = {
            'role': 'Manager',
            'user': self.membership2.user.pk,  # Include the user field
            'team': self.membership2.team.pk,  # Include the team field
        }

        response = self.client.delete(membership_detail_url,update_data, format='json')

        self.membership3.refresh_from_db()
        number_of_memberships_after_deletion = Membership.objects.count()
        # print("number of teams after deletion:",Team.objects.count())


        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(number_of_memberships_before_deletion, number_of_memberships_after_deletion)

    # def test_create_membership_with_authenticated_user(self):

    #     membership_detail_url = reverse('membership-list')  # Replace with the appropriate URL for your team endpoint
    #     login_response = self.client.post(self.login_url, self.user_client1, format='json')
    #     refresh_token = login_response.data['refresh']
    #     refresh = RefreshToken(refresh_token)
    #     new_access_token = str(refresh.access_token)
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')

    #     data = {
    #             'user': self.client2.pk,
    #             'team': self.team3.pk,
    #             'role': 'Manager',
    #             }
    #     number_of_memberships_before_creation = Membership.objects.count()
    #     response = self.client.post(membership_detail_url, data ,format='json')
    #     number_of_memberships_after_creation = Membership.objects.count()
    # #     # self.assertEqual(number_of_memberships_before_creation, number_of_memberships_after_creation-1)
    #     self.assertEqual(response.status_code, 201)
    
    
    


    # def test_create_team_with_unauthenticated_user(self):
    #     team_list_url = reverse('team-list')  # Replace 'team-list' with your actual URL name for team list

    #     login_response = self.client.post(self.login_url, self.user_aunathenticated, format='json')
        

    #     data = {'name': 'New Team'}

    #     number_of_teams_before_creation = Team.objects.count()
    #     response = self.client.post(team_list_url, data, format='json')
    #     number_of_teams_after_creation = Team.objects.count()
    #     # Assert the response and perform further assertions as needed
    #     self.assertEqual(number_of_teams_before_creation, number_of_teams_after_creation)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # 201 represents successful creation


    

    

