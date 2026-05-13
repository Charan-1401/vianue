from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer
from .models import User


def set_token_cookies(response, access, refresh):
    max_age_access = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    max_age_refresh = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    response.set_cookie(
        'vianue_access_token', access,
        max_age=max_age_access, httponly=True,
        samesite='Lax', secure=not settings.DEBUG,
        path='/',
    )
    response.set_cookie(
        'vianue_refresh_token', refresh,
        max_age=max_age_refresh, httponly=True,
        samesite='Lax', secure=not settings.DEBUG,
        path='/api/auth/',
    )


def clear_token_cookies(response):
    response.delete_cookie('vianue_access_token', path='/')
    response.delete_cookie('vianue_refresh_token', path='/api/auth/')


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            set_token_cookies(response, response.data['access'], response.data['refresh'])
        return response


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('vianue_refresh_token')
        if refresh:
            request.data['refresh'] = refresh
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            set_token_cookies(response, response.data['access'], response.data.get('refresh', refresh))
        return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    response = Response({'detail': 'Logged out.'})
    refresh = request.COOKIES.get('vianue_refresh_token')
    if refresh:
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            pass
    clear_token_cookies(response)
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
