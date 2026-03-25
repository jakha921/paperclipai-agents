import django_filters

from .models import GeneratedDocument


class GeneratedDocumentFilter(django_filters.FilterSet):
    class Meta:
        model = GeneratedDocument
        fields = ["template", "employee"]
