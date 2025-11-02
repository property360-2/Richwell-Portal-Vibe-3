from rest_framework.routers import DefaultRouter
from .views import TermViewSet

router = DefaultRouter()
router.register(r"", TermViewSet, basename="term")

urlpatterns = router.urls
