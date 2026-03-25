from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("hemis", views.HEMISSyncViewSet, basename="hemis-sync")
router.register("logs", views.SyncLogViewSet, basename="sync-logs")

urlpatterns = [
    path("", include(router.urls)),
]
