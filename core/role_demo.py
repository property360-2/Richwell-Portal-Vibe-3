from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import make_role_permission

DeanOnly = make_role_permission("DEAN")

class DeanPing(APIView):
    permission_classes = [DeanOnly]

    def get(self, request):
        return Response({"ok": True, "role": "DEAN only"})
