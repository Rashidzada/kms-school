from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "amount", "payment_mode", "reference")
    list_filter = ("category", "payment_mode", "date")
    search_fields = ("reference", "note")

    def log_addition(self, request, object, message):
        try:
            return super().log_addition(request, object, message)
        except Exception:
            try:
                from school.backup_utils import sync_all_postgresql_sequences
                sync_all_postgresql_sequences()
                return super().log_addition(request, object, message)
            except Exception:
                return None

    def log_change(self, request, object, message):
        try:
            return super().log_change(request, object, message)
        except Exception:
            try:
                from school.backup_utils import sync_all_postgresql_sequences
                sync_all_postgresql_sequences()
                return super().log_change(request, object, message)
            except Exception:
                return None

    def log_deletion(self, request, object, object_repr):
        try:
            return super().log_deletion(request, object, object_repr)
        except Exception:
            try:
                from school.backup_utils import sync_all_postgresql_sequences
                sync_all_postgresql_sequences()
                return super().log_deletion(request, object, object_repr)
            except Exception:
                return None
