# rci/rci/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from . import admin as admin_config  # Import admin configuration

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", user_views.dashboard_view, name="home"),
    path("dashboard/", user_views.dashboard_view, name="dashboard"),
    path("login/", user_views.login_view, name="login"),
    path("logout/", user_views.logout_view, name="logout"),
    path("profile/", user_views.profile_view, name="profile"),
    path("users/", include("users.urls")),
    path("admission/", include("admission.urls")),
    path("enrollment/", include("enrollment.urls")),
    path("grades/", include("grades.urls")),
]
