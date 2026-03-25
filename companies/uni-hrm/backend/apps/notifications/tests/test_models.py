"""Тесты моделей notifications."""

import pytest
from django.contrib.auth import get_user_model

from apps.notifications.models import Notification, NotificationTemplate

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com", username="testuser", password="pass123"
    )


@pytest.fixture
def template(db):
    return NotificationTemplate.objects.create(
        code="test_event",
        name="Test Event",
        title={"ru": "Тест", "en": "Test"},
        body={"ru": "Тело", "en": "Body"},
        channels=["in_app"],
    )


@pytest.mark.django_db
def test_notification_template_created(template):
    assert template.code == "test_event"
    assert str(template) == "test_event — Test Event"


@pytest.mark.django_db
def test_notification_created(user):
    notif = Notification.objects.create(
        recipient=user,
        title="Hello",
        message="World",
    )
    assert notif.is_read is False
    assert notif.channel == Notification.Channel.IN_APP
    assert "Hello" in str(notif)


@pytest.mark.django_db
def test_notification_default_ordering(user):
    n1 = Notification.objects.create(recipient=user, title="First", message="m")
    n2 = Notification.objects.create(recipient=user, title="Second", message="m")
    qs = list(Notification.objects.filter(recipient=user))
    assert qs[0].id == n2.id  # newest first
