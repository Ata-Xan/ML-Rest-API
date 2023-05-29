from team_manager.models import Membership, Team
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

class IsMemberOfTheTeam(BasePermission):
    def has_permission(self, request, view):
        User = get_user_model()

        drf_actions = ['update', 'partial_update', 'destroy']

        user = request.user
        # print(view.action)
        if view.action in drf_actions:
            # print(view.action)
            
            team_id = view.kwargs.get('pk')
            team = Team.objects.get(pk=team_id)
            user_role = Membership.objects.filter(user=user, team=team).values('role')
            print("role: ",user_role)
            # print(user_role)
            # to check if the user got any membership at all
            # if view.action in action_role_manager_needed:
            if len(user_role)==0: return False 
            # for update and delete, this rule is applied that the requested user needed to be the 
            # manager of the team.
            if user_role[0]['role']!='Manager':
                return False           
            # print(view.action,user_role)
            return Membership.objects.filter(user=request.user, team=team).exists()
        else:
        # print("View.aciton: ",view.action)
            return True