from django import forms
from school.models import AcademicSession, ClassLevel, Section
from .models import FamilyHousehold, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_no",
            "admission_date",
            "full_name",
            "father_name",
            "dob",
            "gender",
            "tribe_caste",
            "father_occupation",
            "residence",
            "contact_number",
            "profile_picture",
            "current_class",
            "current_section",
            "family",
            "status",
            "remarks",
        ]
        widgets = {
            "admission_date": forms.DateInput(attrs={"type": "date"}),
            "dob": forms.DateInput(attrs={"type": "date"}),
            "residence": forms.Textarea(attrs={"rows": 2}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["admission_no"].required = False
        self.fields["admission_no"].help_text = (
            "Leave blank to auto-generate sequentially (e.g. 1001, 1002...)"
        )


class FamilyHouseholdForm(forms.ModelForm):
    class Meta:
        model = FamilyHousehold
        fields = ["father_guardian_name", "contact_number", "address"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class StudentWithdrawForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "withdrawal_date",
            "class_at_withdrawal",
            "arrears_at_withdrawal",
            "remarks",
        ]
        widgets = {
            "withdrawal_date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }


class SinglePromoteForm(forms.Form):
    target_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(), label="Target Academic Session"
    )
    to_class = forms.ModelChoiceField(
        queryset=ClassLevel.objects.all(), label="Promote to Class"
    )
    to_section = forms.ModelChoiceField(
        queryset=Section.objects.all(), label="Promote to Section"
    )

    def clean(self):
        cleaned_data = super().clean()
        to_class = cleaned_data.get("to_class")
        to_section = cleaned_data.get("to_section")
        if to_class and to_section and to_section.class_level != to_class:
            raise forms.ValidationError("The selected Section does not belong to the selected Class.")
        return cleaned_data
