"""Core application views for the Richwell Portal project."""
from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone


def home(request: HttpRequest) -> HttpResponse:
    """Render the landing page for the portal."""
    context = {
        "project_name": "Richwell College Portal",
        "timestamp": timezone.now(),
    }
    return render(request, "pages/home.html", context)


def healthcheck(_: HttpRequest) -> JsonResponse:
    """Return a minimal JSON payload signalling application health."""
    return JsonResponse({"status": "ok", "timestamp": timezone.now().isoformat()})
