from django import forms
from .models import MonthlySalaryBill, SalaryScale, Teacher


class SalaryScaleForm(forms.ModelForm):
    class Meta:
        model = SalaryScale
        fields = [
            "name",
            "basic_pay",
            "medical_allowance",
            "conveyance_allowance",
            "other_allowances",
        ]


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "full_name",
            "father_name",
            "cnic",
            "dob",
            "qualification",
            "experience",
            "contact_number",
            "address",
            "joining_date",
            "designation",
            "salary_scale",
            "profile_picture",
            "status",
            "remarks",
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "qualification": forms.Textarea(attrs={"rows": 2}),
            "experience": forms.Textarea(attrs={"rows": 2}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class MonthlySalaryBillForm(forms.ModelForm):
    class Meta:
        model = MonthlySalaryBill
        fields = [
            "days_present",
            "allowances",
            "deductions",
            "is_paid",
            "payment_date",
            "voucher_no",
        ]
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }


class GenerateSalaryBillsForm(forms.Form):
    MONTH_CHOICES = [(i, f"Month {i}") for i in range(1, 13)]
    month = forms.ChoiceField(choices=MONTH_CHOICES, label="Month")
    year = forms.IntegerField(label="Year", initial=2026)
