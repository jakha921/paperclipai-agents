from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.departments.urls")),
    path("api/v1/leaves/", include("apps.leaves.urls")),
    path("api/v1/attendance/", include("apps.attendance.urls")),
    path("api/v1/payroll/", include("apps.payroll.urls")),
    path("api/v1/recruitment/", include("apps.recruitment.urls")),
    path("api/v1/academic/", include("apps.academic.urls")),
    path("api/v1/appraisals/", include("apps.appraisal.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/documents/", include("apps.documents.urls")),
    path("api/v1/integrations/", include("apps.integrations.urls")),
    path("api/v1/settings/", include("apps.settings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
