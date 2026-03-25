import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.services import OTPService

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!",
    )


@pytest.mark.django_db
class TestOTP:
    def test_generate_otp(self, user):
        otp = OTPService.generate(user)
        assert len(otp.code) == 6
        assert otp.code.isdigit()
        assert not otp.is_used
        assert otp.expires_at > timezone.now()

    def test_verify_otp_success(self, user):
        otp = OTPService.generate(user)
        result = OTPService.verify(user, otp.code)
        assert result is True
        user.refresh_from_db()
        assert user.is_verified is True

    def test_verify_otp_wrong_code(self, user):
        OTPService.generate(user)
        with pytest.raises(ValidationError):
            OTPService.verify(user, "000000")

    def test_verify_otp_expired(self, user):
        otp = OTPService.generate(user)
        otp.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        otp.save()
        with pytest.raises(ValidationError):
            OTPService.verify(user, otp.code)

    def test_verify_otp_max_attempts(self, user):
        otp = OTPService.generate(user)
        for _ in range(3):
            try:
                OTPService.verify(user, "000000")
            except ValidationError:
                pass
        with pytest.raises(ValidationError):
            OTPService.verify(user, otp.code)

    def test_generate_deactivates_previous(self, user):
        otp1 = OTPService.generate(user)
        OTPService.generate(user)
        otp1.refresh_from_db()
        assert otp1.is_used is True
