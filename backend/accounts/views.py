from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AuthRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data or {}
        email = data.get('email')
        name = data.get('name') or data.get('full_name')
        password = data.get('password')

        if not email or not password:
            return Response(
                {'error': 'email and password are required', 'details': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'user already exists', 'details': {'email': ['This email is already registered.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(email=email, password=password, first_name=name or '')

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {'id': user.id, 'email': user.email, 'name': user.first_name},
            },
            status=status.HTTP_201_CREATED,
        )


class AuthLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate

        data = request.data or {}
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {'error': 'invalid credentials', 'details': {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {'id': user.id, 'email': user.email, 'name': user.first_name},
            }
        )


class AuthRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response(
                {'error': 'refresh token required', 'details': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = RefreshToken(refresh)
        return Response({'access': str(token.access_token)})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'id': user.id, 'email': user.email, 'name': user.first_name})

