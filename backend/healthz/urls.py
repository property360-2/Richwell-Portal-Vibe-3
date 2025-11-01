from django.urls import path

from .views import HealthzView

urlpatterns = [
    path("", HealthzView.as_view(), name="healthz"),
]
