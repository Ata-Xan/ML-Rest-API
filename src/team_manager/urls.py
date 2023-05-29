from django.urls import path, include
from rest_framework import routers

# from team_manager.tests import TeamViewSetTestCase
from .viewsets import LoginViewSet, LogoutViewSet, MembershipViewSet, RegistrationViewSet, TeamViewSet, team_viewset, user_viewset
# from .views import LoginView, LogoutView, RegisterView



router = routers.DefaultRouter()
router.register(r'register', RegistrationViewSet, basename='register')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'team', TeamViewSet, basename='team')
router.register(r'membership', MembershipViewSet, basename='membership')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', user_viewset, name='user'),
    # path('teams/', team_viewset, name='team-detail'),
    # path('memberships/', memberships_list, name='memberships'),
    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    # path('register/', RegisterView.as_view(), name='register'),
]