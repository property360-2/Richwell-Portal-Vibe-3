from rest_framework import viewsets
from .models import Subject, SubjectPrerequisite
from .serializers import SubjectSerializer, SubjectPrerequisiteSerializer
from users.permissions import make_role_permission

DeanOnly = make_role_permission("DEAN")

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by("code")
    serializer_class = SubjectSerializer
    permission_classes = [DeanOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        show_archived = self.request.query_params.get("archived") == "true"
        if not show_archived:
            qs = qs.filter(archived=False)
        return qs


class SubjectPrerequisiteViewSet(viewsets.ModelViewSet):
    queryset = SubjectPrerequisite.objects.all()
    serializer_class = SubjectPrerequisiteSerializer
    permission_classes = [DeanOnly]
