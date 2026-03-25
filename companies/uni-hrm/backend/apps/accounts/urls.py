from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    ChangePasswordView,
    DevLoginView,
    GoogleAuthView,
    LoginView,
    MeView,
    OTPVerifyView,
    RegisterView,
    RoleViewSet,
)

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("google/", GoogleAuthView.as_view(), name="auth-google"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("otp/verify/", OTPVerifyView.as_view(), name="auth-otp-verify"),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path("dev-token/", DevLoginView.as_view(), name="auth-dev-token"),
    ]
