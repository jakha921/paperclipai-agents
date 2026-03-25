import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert str(user) == "Test User"

    def test_email_is_unique(self):
        User.objects.create_user(
            username="user1",
            email="test@example.com",
            password="testpass123",
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username="user2",
                email="test@example.com",
                password="testpass123",
            )

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_full_name_property(self):
        user = User(first_name="John", last_name="Doe", email="john@test.com")
        assert user.full_name == "John Doe"

    def test_full_name_fallback_to_email(self):
        user = User(email="john@test.com")
        assert user.full_name == "john@test.com"

    def test_is_verified_default_false(self):
        user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="testpass123",
        )
        assert user.is_verified is False
