from rest_framework.routers import DefaultRouter

from apps.appraisal.views import (
    AppraisalCycleViewSet,
    AppraisalScoreViewSet,
    EmployeeAppraisalViewSet,
    KPIIndicatorViewSet,
    TrainingProgramViewSet,
    TrainingRecordViewSet,
)

router = DefaultRouter()
router.register("cycles", AppraisalCycleViewSet, basename="appraisal-cycles")
router.register("kpis", KPIIndicatorViewSet, basename="kpi-indicators")
router.register(
    "employee-appraisals",
    EmployeeAppraisalViewSet,
    basename="employee-appraisals",
)
router.register("scores", AppraisalScoreViewSet, basename="appraisal-scores")
router.register(
    "training-programs",
    TrainingProgramViewSet,
    basename="training-programs",
)
router.register(
    "training-records",
    TrainingRecordViewSet,
    basename="training-records",
)

urlpatterns = router.urls
