from django import forms
from .models import AcademicSession, ClassLevel, SchoolSetting, Section


class SchoolSettingForm(forms.ModelForm):
    class Meta:
        model = SchoolSetting
        fields = [
            "name",
            "short_name",
            "tagline",
            "address",
            "logo",
            "contact",
            "academic_session_format",
            "receipt_no_prefix",
            "last_receipt_no",
            "passing_percentage",
            "passing_rule",
            "auto_backup_enabled",
            "auto_backup_interval_days",
            "auto_backup_preferred_time",
            "auto_backup_mode",
            "safe_backup_folder",
            "default_backup_email",
            "email_provider",
            "https_api_provider",
            "https_api_key",
            "backup_send_sql",
            "backup_send_excel",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control fw-bold", "placeholder": "e.g. Kohisar Model School & College"}),
            "short_name": forms.TextInput(attrs={"class": "form-control fw-bold", "placeholder": "e.g. KMS or BPS"}),
            "tagline": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Student Information, Fee & Payroll Management System"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Campus Address"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone / Mobile Numbers"}),
            "safe_backup_folder": forms.TextInput(attrs={"class": "form-control fw-bold", "placeholder": "e.g. D:\\School_Backups or E:\\KMS_Backups"}),
            "auto_backup_preferred_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "auto_backup_mode": forms.Select(attrs={"class": "form-select fw-semibold"}),
            "https_api_key": forms.PasswordInput(render_value=True, attrs={"class": "form-control font-monospace", "placeholder": "Optional Resend (re_...) or Brevo (xkeysib-...) API key"}),
        }


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ["name", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = ["name", "level", "monthly_fee"]


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["class_level", "name", "teacher", "class_teacher"]
        labels = {
            "teacher": "Select Section Teacher (From Staff Directory)",
            "class_teacher": "Or Custom Teacher Name (Optional)",
        }

