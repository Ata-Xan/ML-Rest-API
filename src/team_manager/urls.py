from django.urls import path, include
from rest_framework import routers
from .viewsets import UserViewSet, TeamViewSet, MembershipViewSet
from .views import LoginView, LogoutView, RegisterView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'memberships', MembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]