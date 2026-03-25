from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CandidateViewSet, InterviewViewSet, VacancyViewSet

router = DefaultRouter()
router.register("vacancies", VacancyViewSet, basename="vacancy")
router.register("candidates", CandidateViewSet, basename="candidate")
router.register("interviews", InterviewViewSet, basename="interview")

urlpatterns = [
    path("", include(router.urls)),
]
