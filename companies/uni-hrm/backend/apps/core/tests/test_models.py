import uuid

import pytest
from django.db import connection, models

from apps.core.managers import ActiveManager
from apps.core.models import SoftDeleteMixin, TimestampedModel


# Конкретная модель для тестирования абстрактных миксинов
class ConcreteModel(TimestampedModel, SoftDeleteMixin):
    """Тестовая модель для проверки абстрактных миксинов."""

    name = models.CharField(max_length=100)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        app_label = "core"


_table_created = False


@pytest.fixture(autouse=True)
def create_test_table(request, db):
    """Создаём таблицу для тестовой модели с помощью raw SQL."""
    global _table_created
    if not _table_created:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_concretemodel (
                    id CHAR(32) PRIMARY KEY,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    is_deleted BOOL NOT NULL DEFAULT 0,
                    deleted_at DATETIME NULL,
                    name VARCHAR(100) NOT NULL,
                    created_by_id INTEGER NULL REFERENCES auth_user(id),
                    updated_by_id INTEGER NULL REFERENCES auth_user(id)
                )
            """)
        _table_created = True
    yield


class TestTimestampedModel:
    def test_uuid_pk_generation(self):
        obj = ConcreteModel(name="test")
        assert isinstance(obj.id, uuid.UUID)

    def test_uuid_uniqueness(self):
        obj1 = ConcreteModel(name="test1")
        obj2 = ConcreteModel(name="test2")
        assert obj1.id != obj2.id

    def test_created_at_auto_population(self):
        obj = ConcreteModel.objects.create(name="test")
        assert obj.created_at is not None

    def test_updated_at_auto_population(self):
        obj = ConcreteModel.objects.create(name="test")
        assert obj.updated_at is not None

    def test_updated_at_changes_on_save(self):
        obj = ConcreteModel.objects.create(name="test")
        original_updated = obj.updated_at
        obj.name = "updated"
        obj.save()
        obj.refresh_from_db()
        assert obj.updated_at >= original_updated


class TestSoftDeleteMixin:
    def test_soft_delete_sets_is_deleted(self):
        obj = ConcreteModel.objects.create(name="test")
        obj.soft_delete()
        obj.refresh_from_db()
        assert obj.is_deleted is True

    def test_soft_delete_sets_deleted_at(self):
        obj = ConcreteModel.objects.create(name="test")
        obj.soft_delete()
        obj.refresh_from_db()
        assert obj.deleted_at is not None

    def test_restore_resets_is_deleted(self):
        obj = ConcreteModel.objects.create(name="test")
        obj.soft_delete()
        obj.restore()
        obj.refresh_from_db()
        assert obj.is_deleted is False

    def test_restore_resets_deleted_at(self):
        obj = ConcreteModel.objects.create(name="test")
        obj.soft_delete()
        obj.restore()
        obj.refresh_from_db()
        assert obj.deleted_at is None


@pytest.mark.django_db(transaction=True)
class TestActiveManager:
    def test_filters_out_soft_deleted(self):
        ConcreteModel.objects.all().delete()
        ConcreteModel.objects.create(name="active")
        deleted = ConcreteModel.objects.create(name="deleted")
        deleted.soft_delete()

        assert ConcreteModel.active.count() == 1
        assert ConcreteModel.active.first().name == "active"

    def test_includes_all_in_default_manager(self):
        ConcreteModel.objects.all().delete()
        ConcreteModel.objects.create(name="active")
        deleted = ConcreteModel.objects.create(name="deleted")
        deleted.soft_delete()

        assert ConcreteModel.objects.count() == 2
