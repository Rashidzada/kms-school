from django.contrib import admin
from .models import FamilyHousehold, PromotionHistory, Student


@admin.register(FamilyHousehold)
class FamilyHouseholdAdmin(admin.ModelAdmin):
    list_display = ("family_id", "father_guardian_name", "contact_number")
    search_fields = ("family_id", "father_guardian_name", "contact_number")
    actions = ["delete_selected_safely"]

    @admin.action(description="Delete selected families / households safely")
    def delete_selected_safely(self, request, queryset):
        from django.contrib import messages
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"Successfully deleted {count} family/household record(s).",
            messages.SUCCESS,
        )


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
    actions = ["delete_selected_safely"]

    @admin.action(description="Delete selected students (and all related marks & records)")
    def delete_selected_safely(self, request, queryset):
        from django.contrib import messages
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"Successfully deleted {count} student(s) and their associated records.",
            messages.SUCCESS,
        )


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
