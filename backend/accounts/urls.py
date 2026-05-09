from django.urls import path

from .views import AuthRegisterView, AuthLoginView, AuthRefreshView, MeView

urlpatterns = [
    path('auth/register/', AuthRegisterView.as_view(), name='auth-register'),
    path('auth/login/', AuthLoginView.as_view(), name='auth-login'),
    path('auth/refresh/', AuthRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
]

