from django.contrib import admin
from .models import (
    AcademicSession,
    BackupEmailAccount,
    BackupHistoryLog,
    ClassLevel,
    SchoolSetting,
    Section,
)


@admin.register(SchoolSetting)
class SchoolSettingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contact",
        "auto_backup_enabled",
        "auto_backup_interval_days",
        "default_backup_email",
        "backup_send_sql",
        "backup_send_excel",
        "last_auto_backup_at",
        "last_auto_backup_status",
    )
    list_editable = (
        "auto_backup_enabled",
        "auto_backup_interval_days",
        "default_backup_email",
        "backup_send_sql",
        "backup_send_excel",
    )
    fieldsets = (
        ("School Profile & General Settings", {
            "fields": (
                "name",
                "address",
                "logo",
                "contact",
                "academic_session_format",
                "receipt_no_prefix",
                "last_receipt_no",
                "passing_percentage",
                "passing_rule",
            )
        }),
        ("Automated Daily Cloud Email Backup (.sql & Master .xlsx)", {
            "description": (
                "Configure Automatic 1-Day Cloud Email Backup. "
                "Manage the 3 Sender/Receiver Email & App Password accounts in 'Backup Email & App Password Accounts (3 Options)'."
            ),
            "fields": (
                "auto_backup_enabled",
                "auto_backup_interval_days",
                "default_backup_email",
                "backup_send_sql",
                "backup_send_excel",
                "last_auto_backup_at",
                "last_auto_backup_status",
                "last_auto_backup_message",
            )
        }),
    )


@admin.register(BackupEmailAccount)
class BackupEmailAccountAdmin(admin.ModelAdmin):
    """
    Easy Admin Table where user provides only Email & App Password for up to 3 accounts,
    and checks which ones send or receive the Full SQL + Excel Backup.
    """
    list_display = (
        "slot_number",
        "account_label",
        "email",
        "app_password",
        "use_as_sender",
        "receive_backup",
        "is_active",
        "last_used_at",
    )
    list_editable = (
        "account_label",
        "email",
        "app_password",
        "use_as_sender",
        "receive_backup",
        "is_active",
    )
    list_display_links = ("slot_number",)

    def changelist_view(self, request, extra_context=None):
        BackupEmailAccount.ensure_three_slots()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(BackupHistoryLog)
class BackupHistoryLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "backup_type",
        "status",
        "sender_email",
        "recipient_emails",
        "sql_filename",
        "excel_filename",
    )
    list_filter = ("status", "backup_type")
    search_fields = ("sender_email", "recipient_emails", "details")


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
    list_display = ("name", "class_level", "class_teacher", "teacher")
    list_editable = ("class_teacher", "teacher")
    list_filter = ("class_level",)

