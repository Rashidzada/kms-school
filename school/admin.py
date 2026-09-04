from django.contrib import admin
from .models import AcademicSession, ClassLevel, SchoolSetting, Section


@admin.register(SchoolSetting)
class SchoolSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "receipt_no_prefix", "last_receipt_no")


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "monthly_fee")
    list_filter = ("level",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "class_level", "class_teacher")
    list_filter = ("class_level",)
