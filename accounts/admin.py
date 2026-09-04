from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "amount", "payment_mode", "reference")
    list_filter = ("category", "payment_mode", "date")
    search_fields = ("reference", "note")
