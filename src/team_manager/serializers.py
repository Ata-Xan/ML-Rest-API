from rest_framework import serializers
from .models import User, Team, Membership
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    refresh = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'refresh', 'access']

    def get_refresh(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh)

    def get_access(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)



# class TeamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Team
#         fields = '__all__'

# class MembershipSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Membership
#         fields = '__all__'
