from django.urls import path
from .views import RegisterView, CookieTokenObtainPairView, CookieTokenRefreshView, logout, me

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout', logout, name='logout'),
    path('me', me, name='me'),
]
