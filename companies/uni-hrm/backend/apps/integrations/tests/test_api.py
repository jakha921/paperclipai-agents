import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.integrations.models import HEMISMapping, SyncConflict, SyncLog

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass123")
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="intuser", email="intuser@test.com", password="pass123"
    )


@pytest.fixture
def sync_log(db):
    return SyncLog.objects.create(sync_type="full", status="success")


@pytest.fixture
def mapping(db):
    return HEMISMapping.objects.create(
        content_type="department",
        local_id="local_100",
        hemis_id="hemis_100",
        sync_status="success",
    )


@pytest.fixture
def conflict(db, mapping):
    return SyncConflict.objects.create(
        mapping=mapping,
        field_name="name",
        local_value="Отдел А",
        hemis_value="Department A",
    )


@pytest.fixture
def resolved_conflict(db, mapping, user):
    return SyncConflict.objects.create(
        mapping=mapping,
        field_name="email",
        local_value="old@test.com",
        hemis_value="new@test.com",
        is_resolved=True,
        resolution="hemis",
        resolved_by=user,
    )


# --- Status endpoint ---


@pytest.mark.django_db
def test_status_no_sync(auth_client):
    response = auth_client.get("/api/v1/integrations/hemis/status_info/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_status_with_sync_log(auth_client, sync_log):
    response = auth_client.get("/api/v1/integrations/hemis/status_info/")
    assert response.status_code == 200
    data = response.json()
    assert data["sync_type"] == "full"
    assert data["status"] == "success"


@pytest.mark.django_db
def test_status_returns_latest_log(auth_client):
    SyncLog.objects.create(sync_type="departments", status="success")
    SyncLog.objects.create(sync_type="employees", status="running")
    response = auth_client.get("/api/v1/integrations/hemis/status_info/")
    assert response.status_code == 200
    data = response.json()
    # Latest log should be returned
    assert data["sync_type"] in ("departments", "employees")


# --- Conflicts endpoint ---


@pytest.mark.django_db
def test_conflicts_list(auth_client):
    response = auth_client.get("/api/v1/integrations/hemis/conflicts/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_conflicts_list_with_data(auth_client, conflict):
    response = auth_client.get("/api/v1/integrations/hemis/conflicts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["field_name"] == "name"


@pytest.mark.django_db
def test_conflicts_filter_unresolved(auth_client, conflict, resolved_conflict):
    response = auth_client.get("/api/v1/integrations/hemis/conflicts/?resolved=false")
    assert response.status_code == 200
    data = response.json()
    assert all(not c["is_resolved"] for c in data)


@pytest.mark.django_db
def test_conflicts_filter_resolved(auth_client, conflict, resolved_conflict):
    response = auth_client.get("/api/v1/integrations/hemis/conflicts/?resolved=true")
    assert response.status_code == 200
    data = response.json()
    assert all(c["is_resolved"] for c in data)


# --- Resolve conflict ---


@pytest.mark.django_db
def test_resolve_conflict_local(auth_client, conflict):
    response = auth_client.post(
        f"/api/v1/integrations/hemis/{conflict.id}/resolve/",
        {"resolution": "local"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_resolved"] is True
    assert data["resolution"] == "local"


@pytest.mark.django_db
def test_resolve_conflict_hemis(auth_client, conflict):
    response = auth_client.post(
        f"/api/v1/integrations/hemis/{conflict.id}/resolve/",
        {"resolution": "hemis"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_resolved"] is True
    assert data["resolution"] == "hemis"


@pytest.mark.django_db
def test_resolve_conflict_invalid_resolution(auth_client, conflict):
    response = auth_client.post(
        f"/api/v1/integrations/hemis/{conflict.id}/resolve/",
        {"resolution": "invalid"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_resolve_conflict_not_found(auth_client):
    import uuid

    fake_id = uuid.uuid4()
    response = auth_client.post(
        f"/api/v1/integrations/hemis/{fake_id}/resolve/",
        {"resolution": "local"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# --- Sync logs endpoint ---


@pytest.mark.django_db
def test_sync_logs_list(auth_client, sync_log):
    response = auth_client.get("/api/v1/integrations/logs/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_sync_logs_list_returns_data(auth_client):
    SyncLog.objects.create(sync_type="departments", status="success")
    SyncLog.objects.create(sync_type="employees", status="error", error_message="Fail")
    response = auth_client.get("/api/v1/integrations/logs/")
    assert response.status_code == 200
    data = response.json()
    results = data.get("results", data)
    assert len(results) >= 2


@pytest.mark.django_db
def test_sync_log_detail(auth_client, sync_log):
    response = auth_client.get(f"/api/v1/integrations/logs/{sync_log.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["sync_type"] == "full"


# --- Run sync endpoint ---


@pytest.mark.django_db
def test_run_sync_full(auth_client):
    response = auth_client.post(
        "/api/v1/integrations/hemis/sync/",
        {"sync_type": "full"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("completed", "queued")


@pytest.mark.django_db
def test_run_sync_departments(auth_client):
    response = auth_client.post(
        "/api/v1/integrations/hemis/sync/",
        {"sync_type": "departments"},
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_run_sync_employees(auth_client):
    response = auth_client.post(
        "/api/v1/integrations/hemis/sync/",
        {"sync_type": "employees"},
        format="json",
    )
    assert response.status_code == 200


# --- Auth required ---


@pytest.mark.django_db
def test_no_auth_status(api_client):
    response = api_client.get("/api/v1/integrations/hemis/status_info/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_no_auth_conflicts(api_client):
    response = api_client.get("/api/v1/integrations/hemis/conflicts/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_no_auth_sync(api_client):
    response = api_client.post("/api/v1/integrations/hemis/sync/", {}, format="json")
    assert response.status_code in (401, 403)
