from django import forms
from school.models import AcademicSession, ClassLevel, Section
from .models import ClassSubject, Exam, Subject


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "session", "start_date", "end_date", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. First Term Examination 2026"}),
            "session": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "order", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. English, Mutalae Quran"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Eng, M.quran"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ["class_level", "subject", "total_marks", "passing_marks", "order"]
        widgets = {
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
            "passing_marks": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Select Excel File (.xlsx)",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".xlsx, .xls"}),
    )
