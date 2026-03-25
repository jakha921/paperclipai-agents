from django.contrib import admin

from .models import Candidate, Interview, Vacancy


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 0
    fields = ["first_name", "last_name", "phone", "stage", "source"]
    show_change_link = True


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    fields = ["interview_type", "scheduled_at", "interviewer", "result"]


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ["__str__", "department", "status", "vacancies_count", "deadline", "created_at"]
    list_filter = ["status", "department"]
    search_fields = ["title"]
    inlines = [CandidateInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ["full_name", "vacancy", "stage", "source", "applied_at"]
    list_filter = ["stage", "source"]
    search_fields = ["first_name", "last_name", "phone", "email"]
    inlines = [InterviewInline]
    readonly_fields = ["applied_at", "created_at", "updated_at"]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ["candidate", "interview_type", "scheduled_at", "interviewer", "result"]
    list_filter = ["interview_type", "result"]
    readonly_fields = ["created_at", "updated_at"]
