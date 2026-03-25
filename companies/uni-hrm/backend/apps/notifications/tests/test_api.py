"""Тесты API notifications."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.notifications.models import Notification

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="api@example.com", username="apiuser", password="pass123")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def notification(user):
    return Notification.objects.create(recipient=user, title="Test", message="Test message")


@pytest.mark.django_db
def test_list_notifications(auth_client, notification):
    response = auth_client.get("/api/v1/notifications/notifications/")
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_unread_count(auth_client, notification):
    response = auth_client.get("/api/v1/notifications/notifications/unread_count/")
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_mark_read(auth_client, notification):
    response = auth_client.post(f"/api/v1/notifications/notifications/{notification.id}/mark_read/")
    assert response.status_code == 200
    assert response.data["is_read"] is True


@pytest.mark.django_db
def test_mark_all_read(auth_client, user):
    Notification.objects.create(recipient=user, title="A", message="a")
    Notification.objects.create(recipient=user, title="B", message="b")
    response = auth_client.post("/api/v1/notifications/notifications/mark_all_read/")
    assert response.status_code == 200
    assert response.data["marked"] == 2


@pytest.mark.django_db
def test_unauthenticated_blocked():
    client = APIClient()
    response = client.get("/api/v1/notifications/notifications/")
    assert response.status_code == 401
