from django import forms
from .models import AcademicSession, ClassLevel, SchoolSetting, Section


class SchoolSettingForm(forms.ModelForm):
    class Meta:
        model = SchoolSetting
        fields = [
            "name",
            "address",
            "logo",
            "contact",
            "academic_session_format",
            "receipt_no_prefix",
            "last_receipt_no",
        ]


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
        fields = ["class_level", "name", "class_teacher"]
