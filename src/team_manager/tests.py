from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from team_manager.serializers import  TeamSerializer
from .models import Membership, Team, User

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.client.force_authenticate(user=self.user)
                # Create some sample teams 
        self.team1 = Team.objects.create(name='Team 1')
        self.team2 = Team.objects.create(name='Team 2')
        self.team3 = Team.objects.create(name='Team 3')

         # Create some sample users
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.user3 = User.objects.create_user(username='user3', password='pass3')


        self.membership1 = Membership.objects.create(user=self.user, team=self.team1, role='Manager')
        self.membership2 = Membership.objects.create(user=self.user, team=self.team2, role='Viewer')

    def test_login(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_logout(self):
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_register(self):
        url = reverse('register')
        data = {'username': 'newuser', 'password': 'newpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

        # Additional assertion to verify the new user in the database
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_user_by_authenticated_user(self):
        url = '/api/user/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
    
    def test_user_by_non_authenticated_user(self):
        self.client.logout()
        url = '/api/user/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
        
class MembershipFilterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        # Create some test teams
        self.team1 = Team.objects.create(name='Team 1')
        self.team2 = Team.objects.create(name='Team 2')
        self.team3 = Team.objects.create(name='Team 3')
        self.team4 = Team.objects.create(name='Team 4')

        self.membership1 = Membership.objects.create(user=self.user1, team=self.team1, role='Manager')
        self.membership2 = Membership.objects.create(user=self.user, team=self.team1, role='Viewer')
        self.membership3 = Membership.objects.create(user=self.user, team=self.team3, role='Manager')
        self.membership4 = Membership.objects.create(user=self.user, team=self.team4, role='Viewer')

    def test_membership_by_authenticated_user(self):
        url = '/api/memberships/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)


    def test_membership_by_non_authenticated_user(self):
        self.client.logout()
        url = '/api/teams/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_membership_by_non_existent_user_id(self):
        response = self.client.get('/membership/?user=123')
        self.assertEqual(response.status_code, 404)

class TeamViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        # Create some test teams
        self.team1 = Team.objects.create(name='Team 1')
        self.team2 = Team.objects.create(name='Team 2')
        self.team3 = Team.objects.create(name='Team 3')
        self.team4 = Team.objects.create(name='Team 4')
        
        # Assign memberships to teams
        self.team1.membership_set.create(user=self.user, role='Manager', team=self.team1)
        self.team2.membership_set.create(user=self.user, role='Viewer', team=self.team2)
        self.team2.membership_set.create(user=self.user, role='Viewer', team=self.team4)

    def test_teams_by_authenticated_user(self):
        # Ensure authenticated user can list teams
        url = '/api/teams/'
        response = self.client.get(url)
        teams = Team.objects.filter(membership__user=self.user)
        serializer = TeamSerializer(teams, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
    
    def test_teams_by_nonauthenticated_user(self):
        # Ensure unauthenticated user cannot list teams
        self.client.logout()
        url = '/api/teams/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)