from django.contrib import admin
from .models import Exam, Subject, ClassSubject, ExamMark


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "session", "start_date", "end_date", "is_active")
    list_filter = ("session", "is_active")
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ("class_level", "subject", "total_marks", "passing_marks", "order")
    list_filter = ("class_level", "subject")
    search_fields = ("class_level__name", "subject__name")


@admin.register(ExamMark)
class ExamMarkAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "class_level", "subject", "obtained_marks", "total_marks", "is_absent")
    list_filter = ("exam", "class_level", "subject", "is_absent")
    search_fields = ("student__full_name", "student__admission_no", "subject__name")
