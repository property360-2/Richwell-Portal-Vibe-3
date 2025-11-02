from django.contrib import admin
from django.urls import path, include
from users.views import LogoutView, login_page, logout_view, dashboard
from core.views import healthz
from users.views import dean_dashboard, dean_courses, dean_subjects, dean_sections

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("auth/", include("users.urls")),
    path("", login_page, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("api/terms/", include("terms.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/subjects/", include("subjects.urls")),
    path("api/sections/", include("sections.urls")),
    path("dashboard/", dean_dashboard, name="dashboard"),
    path("dashboard/courses/", dean_courses, name="dean-courses"),
    path("dashboard/subjects/", dean_subjects, name="dean-subjects"),
    path("dashboard/sections/", dean_sections, name="dean-sections"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),  # JWT API logout
]
