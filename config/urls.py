from django.contrib import admin
from django.urls import path, include
from users.views import login_page, logout_view, dashboard
from core.views import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("auth/", include("users.urls")),
    path("", login_page, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]
