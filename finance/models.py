import uuid
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone


class StudentFeeLedger(models.Model):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fee_ledgers"
    )
    academic_session = models.ForeignKey(
        "school.AcademicSession", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "academic_session")
        ordering = ["-created_at"]
        verbose_name = "Student Fee Ledger"
        verbose_name_plural = "Student Fee Ledgers"

    def __str__(self):
        return f"{self.student.full_name} - {self.academic_session.name}"


class StudentFeeMonthEntry(models.Model):
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

    ledger = models.ForeignKey(
        StudentFeeLedger, on_delete=models.CASCADE, related_name="monthly_entries"
    )
    month = models.IntegerField(choices=MONTH_CHOICES)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    last_payment_date = models.DateField(null=True, blank=True)
    last_receipt_no = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ("ledger", "month")
        ordering = ["month"]
        verbose_name = "Fee Month Entry"
        verbose_name_plural = "Fee Month Entries"

    def __str__(self):
        return f"{self.ledger.student.full_name} - Month {self.month} (Bal: {self.balance})"

    @property
    def total_amount(self):
        return (
            (self.arrears or Decimal("0.00"))
            + (self.monthly_fee or Decimal("0.00"))
            + (self.exam_fee or Decimal("0.00"))
            + (self.other_charges or Decimal("0.00"))
        )

    @property
    def balance(self):
        return self.total_amount - (self.paid_amount or Decimal("0.00"))


class FeePaymentReceipt(models.Model):
    receipt_no = models.CharField(max_length=50, unique=True, blank=True)
    payment_date = models.DateField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    month_entries = models.ManyToManyField(
        StudentFeeMonthEntry, related_name="payments"
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.PROTECT, related_name="payments"
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Fee Payment Receipt"
        verbose_name_plural = "Fee Payment Receipts"

    def __str__(self):
        return f"{self.receipt_no} - {self.student.full_name} ({self.amount_paid})"

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            from school.models import SchoolSetting

            setting = SchoolSetting.objects.select_for_update().first()
            if setting:
                setting.last_receipt_no += 1
                setting.save(update_fields=["last_receipt_no"])
                self.receipt_no = f"{setting.receipt_no_prefix}{setting.last_receipt_no}"
            else:
                self.receipt_no = f"REC-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
