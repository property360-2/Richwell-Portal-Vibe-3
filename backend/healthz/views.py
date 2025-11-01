from datetime import datetime, timezone
from typing import Any

from django.http import JsonResponse
from django.views import View


class HealthzView(View):
    """Return a simple health check payload."""

    def get(self, request, *args, **kwargs):  # type: ignore[override]
        payload: dict[str, Any] = {
            "status": "ok",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        return JsonResponse(payload)
