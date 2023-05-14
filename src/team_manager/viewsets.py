from rest_framework import viewsets, generics
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from team_manager.filters import MembershipFilter, TeamFilter, UserFilter
from .models import User, Team, Membership
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .serializers import UserSerializer, TeamSerializer, MembershipSerializer

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

user = UserViewSet.as_view({'get': 'list'})

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TeamFilter
    
teams_list = TeamViewSet.as_view({'get':'list'})

class MembershipViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Membership.objects.all()
    filterset_class = MembershipFilter
    serializer_class = MembershipSerializer
    filter_backends = [DjangoFilterBackend]

memberships_list = MembershipViewSet.as_view({'get':'list'})
