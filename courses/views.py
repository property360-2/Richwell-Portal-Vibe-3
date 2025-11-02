from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer
from users.permissions import make_role_permission

DeanOnly = make_role_permission("DEAN")

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [DeanOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        show_archived = self.request.query_params.get("archived") == "true"
        if not show_archived:
            qs = qs.filter(archived=False)
        return qs
