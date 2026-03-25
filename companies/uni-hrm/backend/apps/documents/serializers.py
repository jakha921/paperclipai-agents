from rest_framework import serializers

from .models import DocumentTemplate, GeneratedDocument


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "code",
            "output_format",
            "variables_schema",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    employee_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocument
        fields = [
            "id",
            "template",
            "template_name",
            "employee",
            "employee_name",
            "file_url",
            "data",
            "generated_at",
        ]
        read_only_fields = ["id", "generated_at", "file_url"]

    def get_employee_name(self, obj) -> str:
        return str(obj.employee)

    def get_file_url(self, obj) -> str | None:
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class GenerateDocumentSerializer(serializers.Serializer):
    template_code = serializers.CharField()
    employee_id = serializers.CharField()
    extra_data = serializers.JSONField(default=dict)
