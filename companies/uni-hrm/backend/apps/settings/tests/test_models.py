import pytest

from apps.settings.models import SETTINGS_UUID, SystemSettings


@pytest.mark.django_db
class TestSystemSettings:
    def test_get_settings_creates_singleton(self):
        settings = SystemSettings.get_settings()
        assert settings.pk == SETTINGS_UUID
        assert settings.site_name == "Uni-HRM"

    def test_get_settings_returns_existing(self):
        s1 = SystemSettings.get_settings()
        s2 = SystemSettings.get_settings()
        assert s1.pk == s2.pk

    def test_default_values(self):
        settings = SystemSettings.get_settings()
        assert settings.currency == "UZS"
        assert settings.timezone == "Asia/Tashkent"
        assert settings.annual_leave_days == 28
        assert settings.sick_leave_days == 14
        assert settings.smtp_port == 587
        assert settings.smtp_use_tls is True

    def test_str(self):
        settings = SystemSettings.get_settings()
        assert str(settings) == "Uni-HRM"

    def test_update_settings(self):
        settings = SystemSettings.get_settings()
        settings.site_name = "My University HRM"
        settings.save()
        refreshed = SystemSettings.objects.get(pk=SETTINGS_UUID)
        assert refreshed.site_name == "My University HRM"

    def test_working_days_default_is_list(self):
        settings = SystemSettings.get_settings()
        assert isinstance(settings.working_days, list)
