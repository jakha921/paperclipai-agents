from django.urls import path

from .views import SystemSettingsView, TestEmailView

urlpatterns = [
    path("", SystemSettingsView.as_view(), name="system-settings"),
    path("test_email/", TestEmailView.as_view(), name="test-email"),
]
