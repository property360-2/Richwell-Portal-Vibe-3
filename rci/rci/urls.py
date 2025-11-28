from django.contrib import admin
from django.urls import path, include
from users import views as user_views
# Import the temporary view we created earlier
from audit.views import archives_list_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", user_views.dashboard_view, name="home"),
    path("dashboard/", user_views.dashboard_view, name="dashboard"),
    path("login/", user_views.login_view, name="login"),
    path("logout/", user_views.logout_view, name="logout"),
    path("profile/", user_views.profile_view, name="profile"),

    # App Includes
    path("users/", include("users.urls")),
    path("admission/", include("admission.urls")),
    path("enrollment/", include("enrollment.urls")),
    path("grades/", include("grades.urls")),
    path("reports/", include("reports.urls")),
    path("staff/", include("staff.urls")),
    path("audit/", include("audit.urls")),

    # DIRECT PATH for Archives (The fix!)
    # This manually wires up the view so the navbar link works
    path("audit/archives/", archives_list_view, name="archives_list"),
]