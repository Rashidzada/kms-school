from django.contrib import admin
from .models import (
    MonthlySalaryBill,
    SalaryScale,
    Teacher,
    TeacherAttendance,
    TeacherAttendanceSetting,
)


@admin.register(SalaryScale)
class SalaryScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "basic_pay", "total_allowances", "gross_salary")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "teacher_id",
        "full_name",
        "father_name",
        "designation",
        "assigned_section",
        "contact_number",
        "cnic",
        "salary_scale",
        "status",
    )
    list_filter = ("status", "designation", "salary_scale")
    search_fields = ("teacher_id", "full_name", "father_name", "contact_number", "cnic", "assigned_section")
    actions = ["delete_selected_safely"]

    @admin.action(description="Delete selected teachers safely")
    def delete_selected_safely(self, request, queryset):
        from django.contrib import messages
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"Successfully deleted {count} teacher(s) and their related records.",
            messages.SUCCESS,
        )


@admin.register(MonthlySalaryBill)
class MonthlySalaryBillAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "month",
        "year",
        "base_pay",
        "allowances",
        "bonus",
        "late_deductions",
        "absent_deductions",
        "deductions",
        "is_paid",
        "payment_date",
    )
    list_filter = ("year", "month", "is_paid")


@admin.register(TeacherAttendanceSetting)
class TeacherAttendanceSettingAdmin(admin.ModelAdmin):
    list_display = (
        "shift_start_time",
        "shift_end_time",
        "grace_period_minutes",
        "working_hours_per_day",
        "working_days_per_month",
        "late_deduction_type",
    )


@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "date",
        "status",
        "check_in",
        "check_out",
        "late_minutes",
        "deduction_amount",
        "bonus_amount",
        "attendance_method",
    )
    list_filter = ("date", "status", "attendance_method")
    search_fields = ("teacher__teacher_id", "teacher__full_name")

