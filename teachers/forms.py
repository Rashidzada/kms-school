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
            "days_late",
            "days_absent",
            "allowances",
            "bonus",
            "late_deductions",
            "absent_deductions",
            "deductions",
            "paid_amount",
            "is_paid",
            "payment_date",
            "voucher_no",
        ]
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
            "days_present": forms.NumberInput(attrs={"min": 0, "max": 31, "id": "id_days_present"}),
            "days_late": forms.NumberInput(attrs={"min": 0, "max": 31, "id": "id_days_late"}),
            "days_absent": forms.NumberInput(attrs={"min": 0, "max": 31, "id": "id_days_absent"}),
            "allowances": forms.NumberInput(attrs={"step": "0.01", "id": "id_allowances"}),
            "bonus": forms.NumberInput(attrs={"step": "0.01", "id": "id_bonus"}),
            "late_deductions": forms.NumberInput(attrs={"step": "0.01", "id": "id_late_deductions"}),
            "absent_deductions": forms.NumberInput(attrs={"step": "0.01", "id": "id_absent_deductions"}),
            "deductions": forms.NumberInput(attrs={"step": "0.01", "id": "id_deductions"}),
            "paid_amount": forms.NumberInput(attrs={"step": "0.01", "id": "id_paid_amount"}),
        }
        labels = {
            "days_present": "Days Present in Month",
            "days_late": "Days Late",
            "days_absent": "Days Absent",
            "allowances": "Scale / Regular Allowances (PKR)",
            "bonus": "Special Bonus / Incentive (PKR)",
            "late_deductions": "Late Arrival Deductions (PKR)",
            "absent_deductions": "Absent Deductions (PKR)",
            "deductions": "Total Deductions / Final Cuts (PKR)",
            "paid_amount": "Amount Paid / Disbursed (PKR)",
            "is_paid": "Mark Fully Paid (Cleared)",
        }


class GenerateSalaryBillsForm(forms.Form):
    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]
    month = forms.ChoiceField(choices=MONTH_CHOICES, label="Salary Month")
    year = forms.IntegerField(label="Salary Year", initial=2026)
    sync_attendance = forms.BooleanField(
        required=False,
        initial=True,
        label="Auto-calculate from Teacher Attendance Records (Days present, late arrivals, absences, cuts & bonuses)",
    )


class TeacherAttendanceSettingForm(forms.ModelForm):
    class Meta:
        from .models import TeacherAttendanceSetting
        model = TeacherAttendanceSetting
        fields = [
            "shift_start_time",
            "shift_end_time",
            "grace_period_minutes",
            "working_hours_per_day",
            "working_days_per_month",
            "late_deduction_type",
            "late_fixed_penalty",
            "half_day_threshold_minutes",
        ]
        widgets = {
            "shift_start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "shift_end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "grace_period_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "working_hours_per_day": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "1"}),
            "working_days_per_month": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 31}),
            "late_deduction_type": forms.Select(attrs={"class": "form-select"}),
            "late_fixed_penalty": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "half_day_threshold_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 30}),
        }
        labels = {
            "shift_start_time": "Morning Shift Start Time (e.g. 08:00 AM)",
            "shift_end_time": "Shift Closing / End Time (e.g. 12:30 PM)",
            "grace_period_minutes": "Grace Period (Minutes after shift start before late cut)",
            "working_hours_per_day": "Working Hours Per Day (Used to calculate hourly cut rate)",
            "working_days_per_month": "Working Days Division (Days per month, typically 30)",
            "late_deduction_type": "Late Comers Cutting Policy",
            "late_fixed_penalty": "Fixed Late Fine / Cut (PKR, if fixed type selected)",
            "half_day_threshold_minutes": "Half-Day Lateness Threshold (Minutes late to count as half-day)",
        }


class BiometricImportForm(forms.Form):
    attendance_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        help_text="Optional override date if file does not contain dates (defaults to date in file or today)",
    )
    import_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".csv,.xlsx,.xls,.txt"}),
        help_text="Upload CSV or Excel export from Fingerprint / Biometric Device",
    )
    paste_data = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control font-monospace small",
            "rows": 8,
            "placeholder": "Paste tab or comma separated biometric logs here...\nExample:\n10001, 2026-10-08, 08:05, 12:35\nT-001, 2026-10-08, 08:22, 12:30",
        }),
        help_text="Or copy-paste raw logs from biometric machine software",
    )

