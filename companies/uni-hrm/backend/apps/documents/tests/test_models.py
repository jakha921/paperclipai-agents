import pytest

from apps.documents.models import DocumentTemplate


@pytest.mark.django_db
def test_document_template_creation():
    template = DocumentTemplate.objects.create(
        name="Test Template",
        code="test_template",
        template_html="<p>Hello {{ employee }}</p>",
        output_format="pdf",
    )
    assert template.name == "Test Template"
    assert template.code == "test_template"
    assert str(template) == "Test Template"
