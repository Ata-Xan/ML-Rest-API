from django.urls import path, include
from rest_framework import routers
from .viewsets import UserViewSet, TeamViewSet, MembershipViewSet, teams_list, memberships_list, user
from .views import LoginView, LogoutView, RegisterView


router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('user/', user, name='user'),
    path('teams/',teams_list,name='teams'),
    path('memberships/', memberships_list, name='memberships'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]