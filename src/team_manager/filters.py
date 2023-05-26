from django.contrib.auth import get_user_model
from django_filters import FilterSet, ModelChoiceFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


from team_manager.models import Membership, Team, User

class CurrentUserFilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return queryset.filter(id=user.id)


class TeamFilter(FilterSet):
    user = ModelChoiceFilter(queryset=get_user_model().objects.all())

    class Meta:
        model = Team
        fields = ['name']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        queryset = queryset.filter(membership__user=user).distinct()
        return queryset


class MembershipFilter(FilterSet):
    user = ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Membership
        fields = ['user']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        return queryset






























# from django_filters import rest_framework as filters
# from django.db.models import Q
# from team_manager.models import Membership, User, Team
# from django.contrib.auth import get_user_model


# class UserFilter(filters.FilterSet):
#     class Meta:
#         model = User
#         fields = ['id']  # Fields to filter on

#     def filter_queryset(self, queryset):
#         # Filter the queryset to return only the current user
#         user = self.request.user
#         return queryset.filter(id=user.id)


# User = get_user_model()

# class TeamFilter(filters.FilterSet):
#     user = filters.ModelChoiceFilter(queryset=get_user_model().objects.all())

#     class Meta:
#         model = Team
#         fields = ['name']

#     def filter_queryset(self, queryset):
#         queryset = super().filter_queryset(queryset)
#         # print("ata")
#         user = self.request.user
#         # if user.is_authenticated:
#         queryset = queryset.filter(membership__user=user).distinct()
#         # print("len => ", len(queryset))

#         return queryset



# class MembershipFilter(filters.FilterSet):
#     user = filters.ModelChoiceFilter(queryset=User.objects.all())

#     class Meta:
#         model = Membership
#         fields = ['user']

#     def filter_queryset(self, queryset):
#         queryset = super().filter_queryset(queryset)

#         user = self.request.user

#         if user.is_authenticated:
#             queryset = queryset.filter(user=user)

#         return queryset



# # class TeamFilter(filters.FilterSet):
# #     user = filters.ModelChoiceFilter(queryset=User.objects.all())

# #     class Meta:
# #         model = Team
# #         fields = ['name']

# #     def filter_queryset(self, queryset):
# #         queryset = super().filter_queryset(queryset)

# #         if self.request.user.is_authenticated:
# #             queryset = queryset.filter(membership__user=self.request.user)

# #         return queryset