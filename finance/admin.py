from django.contrib import admin
from .models import FeePaymentReceipt, StudentFeeLedger, StudentFeeMonthEntry


class StudentFeeMonthEntryInline(admin.TabularInline):
    model = StudentFeeMonthEntry
    extra = 0
    readonly_fields = ("month", "total_amount", "balance")


@admin.register(StudentFeeLedger)
class StudentFeeLedgerAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_session", "created_at")
    list_filter = ("academic_session",)
    search_fields = ("student__admission_no", "student__full_name")
    inlines = [StudentFeeMonthEntryInline]


@admin.register(FeePaymentReceipt)
class FeePaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "student", "amount_paid", "payment_date")
    search_fields = ("receipt_no", "student__full_name", "student__admission_no")
    list_filter = ("payment_date",)
