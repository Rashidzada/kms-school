from django.contrib import admin
from .models import MonthlySalaryBill, SalaryScale, Teacher


@admin.register(SalaryScale)
class SalaryScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "basic_pay", "total_allowances", "gross_salary")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "teacher_id",
        "full_name",
        "designation",
        "salary_scale",
        "status",
        "contact_number",
    )
    list_filter = ("status", "designation", "salary_scale")
    search_fields = ("teacher_id", "full_name", "contact_number", "cnic")


@admin.register(MonthlySalaryBill)
class MonthlySalaryBillAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "month",
        "year",
        "base_pay",
        "allowances",
        "deductions",
        "is_paid",
        "payment_date",
    )
    list_filter = ("year", "month", "is_paid")
