from django.urls import path, include
from rest_framework import routers
from .viewsets import UserViewSet, TeamViewSet, MembershipViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'memberships', MembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]