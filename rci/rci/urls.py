# rci/rci/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import admin as admin_config  # Import admin configuration

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="dashboard.html"), name="home"),
    path("users/", include("users.urls")),
]
