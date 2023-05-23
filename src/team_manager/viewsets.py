from rest_framework import viewsets, generics
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from team_manager.filters import MembershipFilter, TeamFilter, UserFilter
from .models import User, Team, Membership
from .serializers import UserSerializer, TeamSerializer, MembershipSerializer

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfTheTeam]
    authentication_classes = [SessionAuthentication]
    filter_backends = [DjangoFilterBackend]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TeamViewSet(BaseViewSet):
    queryset = Team.objects.all()
    filterset_class = TeamFilter
    serializer_class = TeamSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = TeamFilter
    
teams_list = TeamViewSet.as_view({'get':'list'})

class MembershipViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_backends = [DjangoFilterBackend]

memberships_list = MembershipViewSet.as_view({'get':'list'})
