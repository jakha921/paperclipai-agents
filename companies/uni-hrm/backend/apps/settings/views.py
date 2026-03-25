from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsSuperAdmin

from .models import SystemSettings
from .serializers import SystemSettingsSerializer


class SystemSettingsView(APIView):
    """Singleton settings endpoint — GET retrieves, PATCH updates."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsSuperAdmin()]

    def get(self, request: Request) -> Response:
        settings = SystemSettings.get_settings()
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        settings = SystemSettings.get_settings()
        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TestEmailView(APIView):
    """Send a test email using current SMTP settings."""

    permission_classes = [IsSuperAdmin]

    def post(self, request: Request) -> Response:
        settings_obj = SystemSettings.get_settings()
        to_email = request.data.get("to_email", request.user.email)
        if not to_email:
            return Response({"error": "No recipient email"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            send_mail(
                subject=f"Test Email from {settings_obj.site_name}",
                message="This is a test email from your Uni-HRM system.",
                from_email=settings_obj.from_email or "noreply@uni-hrm.uz",
                recipient_list=[to_email],
                fail_silently=False,
            )
            return Response({"message": f"Test email sent to {to_email}"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
