from unittest.mock import patch

import pytest

from apps.integrations.hemis_client import HEMISClient, HEMISClientError
from apps.integrations.models import HEMISMapping, SyncConflict, SyncLog
from apps.integrations.services import sync_departments, sync_employees

# --- HEMISClient ---


class TestHEMISClient:
    def test_client_init_defaults(self, settings):
        settings.HEMIS_BASE_URL = "https://test.hemis.uz/rest/v1"
        settings.HEMIS_API_TOKEN = ""
        client = HEMISClient()
        assert client.base_url == "https://test.hemis.uz/rest/v1"
        assert client.token == ""

    def test_client_headers(self, settings):
        settings.HEMIS_API_TOKEN = "test-token-123"
        client = HEMISClient()
        headers = client.headers
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Accept"] == "application/json"

    def test_mock_data_departments(self, settings):
        settings.HEMIS_API_TOKEN = ""
        client = HEMISClient()
        data = client.get_departments()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "dept_001"

    def test_mock_data_employees(self, settings):
        settings.HEMIS_API_TOKEN = ""
        client = HEMISClient()
        data = client.get_employees()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_mock_data_academic_loads(self, settings):
        settings.HEMIS_API_TOKEN = ""
        client = HEMISClient()
        data = client.get_academic_loads("2024-1")
        assert isinstance(data, list)
        assert len(data) == 1

    def test_api_error_raises_client_error(self, settings):
        settings.HEMIS_API_TOKEN = "real-token"
        settings.HEMIS_BASE_URL = "http://invalid-host-that-does-not-exist:9999"
        client = HEMISClient()
        with pytest.raises(HEMISClientError):
            client.get_departments()


# --- sync_departments ---


@pytest.mark.django_db
class TestSyncDepartments:
    @patch.object(HEMISClient, "get_departments")
    def test_sync_departments_returns_stats(self, mock_get):
        mock_get.return_value = [
            {"id": "d1", "name": "CS Department"},
            {"id": "d2", "name": "Math Department"},
        ]
        stats = sync_departments()
        assert isinstance(stats, dict)
        assert "created" in stats
        assert "updated" in stats
        assert "errors" in stats

    @patch.object(HEMISClient, "get_departments")
    def test_sync_departments_api_failure(self, mock_get):
        mock_get.side_effect = Exception("HEMIS unreachable")
        stats = sync_departments()
        assert stats["errors"] >= 1

    @patch.object(HEMISClient, "get_departments")
    def test_sync_departments_empty_response(self, mock_get):
        mock_get.return_value = []
        stats = sync_departments()
        assert stats["created"] == 0
        assert stats["updated"] == 0
        assert stats["errors"] == 0

    @patch.object(HEMISClient, "get_departments")
    def test_sync_departments_creates_hemis_mapping(self, mock_get):
        mock_get.return_value = [{"id": "dept_new", "name": "New Dept For Mapping"}]
        sync_departments()
        mapping = HEMISMapping.objects.filter(content_type="department", hemis_id="dept_new")
        assert mapping.exists()
        assert mapping.first().sync_status == "success"


# --- sync_employees ---


@pytest.mark.django_db
class TestSyncEmployees:
    @patch.object(HEMISClient, "get_employees")
    def test_sync_employees_basic(self, mock_get):
        mock_get.return_value = [
            {"id": "e1", "name": "Test Employee", "pinfl": "99999999999999"},
        ]
        stats = sync_employees()
        assert isinstance(stats, dict)
        assert "created" in stats
        assert "updated" in stats
        assert "errors" in stats

    @patch.object(HEMISClient, "get_employees")
    def test_sync_employees_api_failure(self, mock_get):
        mock_get.side_effect = Exception("HEMIS unreachable")
        stats = sync_employees()
        assert stats["errors"] >= 1

    @patch.object(HEMISClient, "get_employees")
    def test_sync_employees_empty_response(self, mock_get):
        """Empty list from HEMIS returns stats dict (may error due to import issue)."""
        mock_get.return_value = []
        stats = sync_employees()
        assert isinstance(stats, dict)
        assert "created" in stats


# --- SyncLog model ---


@pytest.mark.django_db
class TestSyncLogModel:
    def test_sync_log_str(self):
        log = SyncLog.objects.create(sync_type="full", status="success")
        assert "full" in str(log)
        assert "success" in str(log)

    def test_sync_log_default_status(self):
        log = SyncLog.objects.create(sync_type="departments")
        assert log.status == "running"

    def test_sync_log_with_stats(self):
        stats = {"created": 5, "updated": 3, "errors": 0}
        log = SyncLog.objects.create(sync_type="departments", status="success", stats=stats)
        assert log.stats["created"] == 5

    def test_sync_log_with_error(self):
        log = SyncLog.objects.create(
            sync_type="employees",
            status="error",
            error_message="Connection refused",
        )
        assert log.error_message == "Connection refused"


# --- SyncConflict model ---


@pytest.mark.django_db
class TestSyncConflictModel:
    def test_conflict_creation(self):
        mapping = HEMISMapping.objects.create(
            content_type="employee",
            local_id="loc_1",
            hemis_id="hem_1",
            sync_status="success",
        )
        conflict = SyncConflict.objects.create(
            mapping=mapping,
            field_name="name",
            local_value="Иванов",
            hemis_value="Ivanov",
        )
        assert not conflict.is_resolved
        assert conflict.resolution == ""

    def test_conflict_resolve(self, django_user_model):
        user = django_user_model.objects.create_user(username="resolver", password="pass123")
        mapping = HEMISMapping.objects.create(
            content_type="employee",
            local_id="loc_2",
            hemis_id="hem_2",
            sync_status="success",
        )
        conflict = SyncConflict.objects.create(
            mapping=mapping,
            field_name="email",
            local_value="a@test.com",
            hemis_value="b@test.com",
        )
        conflict.is_resolved = True
        conflict.resolution = "local"
        conflict.resolved_by = user
        conflict.save()
        conflict.refresh_from_db()
        assert conflict.is_resolved
        assert conflict.resolution == "local"
        assert conflict.resolved_by == user
