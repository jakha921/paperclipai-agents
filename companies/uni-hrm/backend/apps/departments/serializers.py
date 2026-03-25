from rest_framework import serializers

from .models import Department, Employee, EmploymentHistory, Position


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            "id",
            "name",
            "code",
            "category",
            "min_salary",
            "max_salary",
            "is_academic",
            "requirements",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class DepartmentListSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True)
    name_display = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "name_display",
            "code",
            "department_type",
            "is_active",
            "parent",
            "employee_count",
            "level",
            "lft",
            "rght",
            "tree_id",
        ]

    def get_name_display(self, obj: Department) -> str:
        request = self.context.get("request")
        lang = getattr(request, "LANGUAGE_CODE", "ru") if request else "ru"
        return obj.get_name(lang)


class DepartmentSerializer(DepartmentListSerializer):
    children = serializers.SerializerMethodField()

    class Meta(DepartmentListSerializer.Meta):
        fields = DepartmentListSerializer.Meta.fields + ["children"]

    def get_children(self, obj: Department) -> list:
        if not obj.is_leaf_node():
            serializer = DepartmentListSerializer(
                obj.get_children().filter(is_active=True),
                many=True,
                context=self.context,
            )
            return serializer.data
        return []


class EmploymentHistorySerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()

    class Meta:
        model = EmploymentHistory
        fields = [
            "id",
            "department",
            "department_name",
            "position",
            "position_name",
            "start_date",
            "end_date",
            "order_number",
            "order_date",
            "change_reason",
        ]

    def get_department_name(self, obj: EmploymentHistory) -> str:
        return obj.department.get_name()

    def get_position_name(self, obj: EmploymentHistory) -> str:
        return obj.position.name.get("ru", "")


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_number",
            "full_name",
            "first_name",
            "last_name",
            "middle_name",
            "department",
            "department_name",
            "position",
            "position_name",
            "status",
            "contract_type",
            "hire_date",
            "phone",
            "email",
            "photo",
        ]

    def get_department_name(self, obj: Employee) -> str:
        return obj.department.get_name()

    def get_position_name(self, obj: Employee) -> str:
        return obj.position.name.get("ru", "")


class EmployeeDetailSerializer(EmployeeListSerializer):
    history = EmploymentHistorySerializer(many=True, read_only=True)
    department_data = DepartmentListSerializer(source="department", read_only=True)
    position_data = PositionSerializer(source="position", read_only=True)

    class Meta(EmployeeListSerializer.Meta):
        fields = EmployeeListSerializer.Meta.fields + [
            "user",
            "pinfl",
            "inn",
            "passport_series",
            "birth_date",
            "gender",
            "nationality",
            "address",
            "history",
            "department_data",
            "position_data",
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "user",
            "department",
            "position",
            "hire_date",
            "contract_type",
            "first_name",
            "last_name",
            "middle_name",
            "pinfl",
            "inn",
            "passport_series",
            "birth_date",
            "gender",
            "nationality",
            "phone",
            "email",
            "address",
            "photo",
        ]

    def validate(self, attrs: dict) -> dict:
        return attrs
