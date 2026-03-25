from rest_framework.routers import DefaultRouter

from apps.academic import views

router = DefaultRouter()
router.register("degrees", views.AcademicDegreeViewSet, basename="academic-degrees")
router.register("titles", views.AcademicTitleViewSet, basename="academic-titles")
router.register(
    "employee-academic",
    views.EmployeeAcademicViewSet,
    basename="employee-academic",
)
router.register("subjects", views.SubjectViewSet, basename="subjects")
router.register("loads", views.AcademicLoadViewSet, basename="academic-loads")
router.register("contests", views.PositionContestViewSet, basename="position-contests")

urlpatterns = router.urls
