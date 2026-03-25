from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("templates", views.DocumentTemplateViewSet, basename="document-templates")
router.register("documents", views.GeneratedDocumentViewSet, basename="generated-documents")
router.register("reports", views.ReportViewSet, basename="reports")
router.register("analytics", views.AnalyticsViewSet, basename="analytics")

urlpatterns = [
    path("", include(router.urls)),
]
