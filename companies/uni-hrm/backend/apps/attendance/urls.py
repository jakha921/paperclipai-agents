from rest_framework.routers import DefaultRouter

from apps.attendance.views import (
    AttendanceRecordViewSet,
    EmployeeScheduleViewSet,
    TimeSheetViewSet,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register("schedules", WorkScheduleViewSet, basename="work-schedules")
router.register("employee-schedules", EmployeeScheduleViewSet, basename="employee-schedules")
router.register("records", AttendanceRecordViewSet, basename="attendance-records")
router.register("timesheets", TimeSheetViewSet, basename="timesheets")

urlpatterns = router.urls
