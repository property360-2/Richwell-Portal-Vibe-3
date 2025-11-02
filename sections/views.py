from rest_framework import viewsets
from .models import Section, AssignedSubject
from .serializers import SectionSerializer, AssignedSubjectSerializer
from users.permissions import make_role_permission

DeanOnly = make_role_permission("DEAN")

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all().order_by("code")
    serializer_class = SectionSerializer
    permission_classes = [DeanOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        show_archived = self.request.query_params.get("archived") == "true"
        if not show_archived:
            qs = qs.filter(archived=False)
        return qs


class AssignedSubjectViewSet(viewsets.ModelViewSet):
    queryset = AssignedSubject.objects.all()
    serializer_class = AssignedSubjectSerializer
    permission_classes = [DeanOnly]
