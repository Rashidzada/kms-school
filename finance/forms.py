from decimal import Decimal
from django import forms
from .models import FeePaymentReceipt, StudentFeeMonthEntry


class FeeCollectForm(forms.Form):
    selected_months = forms.ModelMultipleChoiceField(
        queryset=StudentFeeMonthEntry.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Months to Pay",
    )
    amount_paid = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Amount Paid (PKR)"
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Payment Date"
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Optional payment remarks / notes"}),
        label="Remarks",
    )

    def __init__(self, ledger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ledger:
            self.fields["selected_months"].queryset = (
                ledger.monthly_entries.filter(is_paid=False).order_by("month")
            )


class FamilyFeePaymentForm(forms.Form):
    selected_months = forms.ModelMultipleChoiceField(
        queryset=StudentFeeMonthEntry.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Month Entries to Pay",
    )
    amount_paid = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Total Amount Paid (PKR)"
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Payment Date"
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Optional payment notes"}),
        label="Remarks",
    )

    def __init__(self, family=None, active_session=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if family and active_session:
            students = family.students.filter(status="Active")
            self.fields["selected_months"].queryset = (
                StudentFeeMonthEntry.objects.filter(
                    ledger__student__in=students,
                    ledger__academic_session=active_session,
                    is_paid=False,
                )
                .select_related("ledger__student")
                .order_by("ledger__student", "month")
            )


class FeeAdjustmentForm(forms.Form):
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
    from_month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label="Apply Monthly Fee From Month",
        help_text="This new fee will apply to this month and all future months in the session.",
    )
    new_monthly_fee = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, label="New Monthly Fee (PKR)"
    )
    single_month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label="Target Specific Month for Charges",
        required=False,
    )
    exam_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal("0.00"),
        label="Exam Fee (Single Month)",
    )
    other_charges = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal("0.00"),
        label="Other Charges (Single Month)",
    )
