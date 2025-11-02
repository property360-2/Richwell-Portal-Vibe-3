from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import HybridLoginView, MeView, LogoutView

urlpatterns = [
    path("login/", HybridLoginView.as_view(), name="auth-login"),  # hybrid login
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="users-me"),
]
