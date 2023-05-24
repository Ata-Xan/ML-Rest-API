
from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer

class RegistrationViewSet(viewsets.ViewSet):
    def create(self, request):
        
        serializer = UserSerializer(data=request.data)

        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

class LoginViewSet(viewsets.ViewSet):
    

    def create(self, request):
        if request.user.is_authenticated:
            return Response({"detail": "You are already logged in"}, status=status.HTTP_400_BAD_REQUEST)
        username = request.data.get("email")
        password = request.data.get("password")
 
        if not username:
            return Response(
                {"detail": "email is not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif not password:
            return Response(
                {"detail": "password is not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )



class LogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
































# logger = logging.getLogger(__name__)
# class BaseViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated, IsMemberOfTheTeam]
#     authentication_classes = [SessionAuthentication]
#     # filter_backends = [DjangoFilterBackend]



# class UserViewSet(ViewSet):
#     @action(methods=['post'], detail=False)
#     def register(self, request):
#         serializer = UserRegistrationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         refresh = RefreshToken.for_user(user)
#         return Response(
#             {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             },
#             status=status.HTTP_201_CREATED,
#         )

#     @action(methods=['post'], detail=False)
#     def login(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = authenticate(
#             username=serializer.validated_data['username'],
#             password=serializer.validated_data['password'],
#         )

#         if user is None:
#             raise AuthenticationFailed('Invalid username or password')

#         refresh = RefreshToken.for_user(user)
#         return Response(
#             {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             },
#             status=status.HTTP_200_OK,
#         )

#     @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
#     def logout(self, request):
#         refresh_token = request.data['refresh_token']
#         try:
#             token = RefreshToken(refresh_token)
#             if token.is_valid():
#                 token.blacklist()
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#             else:
#                 raise AuthenticationFailed('Invalid refresh token')
#         except Exception as e:
#             logger.exception('Error logging out user')
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class UserViewSet(LoginView, LogoutView, RegisterView):

#     def login(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = User.objects.filter(username=username).first()
#         if user is None or not user.check_password(password):
#             return HttpResponseBadRequest('Invalid username or password')
#         token = Token.objects.create(user=user)
#         return HttpResponse({'token': token.key})

#     def logout(self, request):
#         token = request.headers.get('Authorization')
#         if token is None:
#             return HttpResponseBadRequest('No token provided')
#         try:
#             token.delete()
#         except Token.DoesNotExist:
#             pass
#         return HttpResponse('Successfully logged out')

#     def register(self, request):
#         username = request.data.get('username')
#         email = request.data.get('email')
#         password = request.data.get('password')
#         if User.objects.filter(username=username).exists():
#             return HttpResponseBadRequest('Username already exists')
#         if User.objects.filter(email=email).exists():
#             return HttpResponseBadRequest('Email already exists')
#         user = User.objects.create_user(username, email, password)
#         return HttpResponse('Successfully registered')


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class TeamViewSet(BaseViewSet):
#     queryset = Team.objects.all()
#     filterset_class = TeamFilter
#     serializer_class = TeamSerializer
#     authentication_classes = [SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     filterset_class = TeamFilter
    
# teams_list = TeamViewSet.as_view({'get':'list'})

# class MembershipViewSet(viewsets.ModelViewSet):
#     authentication_classes = [SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = Membership.objects.all()
#     serializer_class = MembershipSerializer
#     filter_backends = [DjangoFilterBackend]

# memberships_list = MembershipViewSet.as_view({'get':'list'})
