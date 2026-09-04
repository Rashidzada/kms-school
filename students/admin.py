from django.contrib import admin
from .models import FamilyHousehold, PromotionHistory, Student


@admin.register(FamilyHousehold)
class FamilyHouseholdAdmin(admin.ModelAdmin):
    list_display = ("family_id", "father_guardian_name", "contact_number")
    search_fields = ("family_id", "father_guardian_name", "contact_number")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "admission_no",
        "full_name",
        "father_name",
        "current_class",
        "current_section",
        "status",
    )
    list_filter = ("status", "current_class", "current_section", "gender")
    search_fields = ("admission_no", "full_name", "father_name", "contact_number")


@admin.register(PromotionHistory)
class PromotionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "from_class",
        "to_class",
        "from_section",
        "to_section",
        "session",
        "promotion_date",
    )
    list_filter = ("session", "from_class", "to_class")
