from rest_framework import viewsets
from .models import Term
from .serializers import TermSerializer
from users.permissions import make_role_permission

DeanOnly = make_role_permission("DEAN")

class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all().order_by("-id")
    serializer_class = TermSerializer
    permission_classes = [DeanOnly]
