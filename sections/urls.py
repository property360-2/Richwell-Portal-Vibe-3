from rest_framework.routers import DefaultRouter
from .views import SectionViewSet, AssignedSubjectViewSet

router = DefaultRouter()
router.register(r"", SectionViewSet, basename="section")
router.register(r"assigned", AssignedSubjectViewSet, basename="assigned-subject")

urlpatterns = router.urls
