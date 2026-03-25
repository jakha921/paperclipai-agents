from django.contrib import admin

from .models import DocumentTemplate, GeneratedDocument


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "output_format", "is_active"]
    list_filter = ["output_format", "is_active"]
    search_fields = ["name", "code"]


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ["template", "employee", "generated_at", "generated_by"]
    list_filter = ["template"]
    raw_id_fields = ["employee", "generated_by"]
