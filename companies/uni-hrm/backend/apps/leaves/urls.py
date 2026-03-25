from rest_framework.routers import DefaultRouter

from apps.leaves.views import (
    LeaveAllocationViewSet,
    LeaveRequestViewSet,
    LeaveTypeViewSet,
    PublicHolidayViewSet,
)

router = DefaultRouter()
router.register("types", LeaveTypeViewSet, basename="leave-types")
router.register("allocations", LeaveAllocationViewSet, basename="leave-allocations")
router.register("requests", LeaveRequestViewSet, basename="leave-requests")
router.register("holidays", PublicHolidayViewSet, basename="public-holidays")

urlpatterns = router.urls
