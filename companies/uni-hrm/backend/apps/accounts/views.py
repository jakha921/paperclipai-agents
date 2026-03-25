from django.conf import settings
from django.utils.translation import gettext_lazy as _
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    RoleSerializer,
    UserSerializer,
)
from apps.accounts.services import OTPService


class LoginThrottle(AnonRateThrottle):
    rate = "5/min"


class OTPThrottle(AnonRateThrottle):
    rate = "3/min"


def _get_tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(APIView):
    """Вход по email и паролю. Возвращает JWT токены."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = _get_tokens_for_user(user)
        return Response(
            {
                **tokens,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    """Регистрация нового пользователя. Возвращает JWT токены."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = _get_tokens_for_user(user)
        return Response(
            {
                **tokens,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """Получение и обновление профиля текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """Смена пароля текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": _("Пароль успешно изменён.")})


class OTPVerifyView(APIView):
    """Верификация пользователя по OTP коду."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPThrottle]

    def post(self, request: Request) -> Response:
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OTPService.verify(request.user, serializer.validated_data["code"])
        return Response({"detail": _("Верификация прошла успешно.")})


class RoleViewSet(viewsets.ModelViewSet):
    """CRUD для ролей. Доступно только администраторам."""

    queryset = Role.objects.prefetch_related("permissions").all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]


class GoogleAuthView(APIView):
    """Аутентификация через Google OAuth2. Принимает credential от Google One Tap."""

    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        credential = request.data.get("credential")
        if not credential:
            return Response(
                {"error": "credential обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload = id_token.verify_oauth2_token(
                credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {"error": "Неверный Google токен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = payload.get("email", "").lower()
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": payload.get("given_name", ""),
                "last_name": payload.get("family_name", ""),
                "is_verified": True,
            },
        )
        tokens = _get_tokens_for_user(user)
        return Response(
            {
                **tokens,
                "user": UserSerializer(user).data,
            },
        )


class DevLoginView(APIView):
    """Dev-only: вход под любой ролью без пароля. Работает только при DEBUG=True."""

    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        if not settings.DEBUG:
            return Response(
                {"error": "Недоступно в production"},
                status=status.HTTP_403_FORBIDDEN,
            )
        role = request.data.get("role", "super_admin")
        if role == "superuser":
            user = User.objects.filter(is_superuser=True, is_active=True).first()
        else:
            user = User.objects.filter(user_roles__role__code=role, is_active=True).first()
        if not user:
            return Response(
                {"error": f"Нет пользователя с ролью '{role}'"},
                status=status.HTTP_404_NOT_FOUND,
            )
        tokens = _get_tokens_for_user(user)
        return Response(
            {
                **tokens,
                "user": UserSerializer(user).data,
            },
        )
