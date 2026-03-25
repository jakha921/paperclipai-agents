from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import Permission, Role, User


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(_("Неверный email или пароль."))
        if not user.is_active:
            raise serializers.ValidationError(_("Аккаунт деактивирован."))
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password", "password_confirm"]

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": _("Пароли не совпадают.")})
        return attrs

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        # Генерируем username из email
        validated_data["username"] = validated_data["email"].split("@")[0]
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "language",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "is_verified", "date_joined"]


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Неверный текущий пароль."))
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Сериализатор верификации OTP."""

    code = serializers.CharField(max_length=6, min_length=6)


class PermissionSerializer(serializers.ModelSerializer):
    """Сериализатор разрешения."""

    class Meta:
        model = Permission
        fields = ["id", "codename", "name", "module"]


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор роли с вложенными разрешениями."""

    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source="permissions",
        required=False,
    )

    class Meta:
        model = Role
        fields = ["id", "name", "code", "description", "level", "permissions", "permission_ids"]

    def create(self, validated_data: dict) -> Role:
        permissions = validated_data.pop("permissions", [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permissions)
        return role

    def update(self, instance: Role, validated_data: dict) -> Role:
        permissions = validated_data.pop("permissions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance
