import pytest

from apps.integrations.models import HEMISMapping, SyncLog


@pytest.mark.django_db
def test_hemis_mapping_creation():
    mapping = HEMISMapping.objects.create(
        content_type="department",
        local_id="local_001",
        hemis_id="hemis_001",
        sync_status="success",
    )
    assert mapping.content_type == "department"
    assert mapping.hemis_id == "hemis_001"


@pytest.mark.django_db
def test_sync_log_creation():
    log = SyncLog.objects.create(
        sync_type="departments",
        status="running",
    )
    assert log.sync_type == "departments"
    assert log.status == "running"
