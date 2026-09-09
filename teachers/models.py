from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils import timezone


class SalaryScale(models.Model):
    name = models.CharField(max_length=100, unique=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    medical_allowance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    conveyance_allowance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    other_allowances = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Salary Scale"
        verbose_name_plural = "Salary Scales"

    def __str__(self):
        return f"{self.name} (Basic: {self.basic_pay})"

    @property
    def total_allowances(self):
        return (
            (self.medical_allowance or Decimal("0.00"))
            + (self.conveyance_allowance or Decimal("0.00"))
            + (self.other_allowances or Decimal("0.00"))
        )

    @property
    def gross_salary(self):
        return (self.basic_pay or Decimal("0.00")) + self.total_allowances


class Teacher(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    teacher_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, blank=True)
    cnic = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True, default=timezone.now)
    qualification = models.TextField(blank=True, default="")
    experience = models.TextField(blank=True, default="")
    contact_number = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")
    joining_date = models.DateField(default=timezone.now)
    designation = models.CharField(max_length=100)
    salary_scale = models.ForeignKey(
        SalaryScale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
    )
    profile_picture = models.ImageField(upload_to="teachers/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["teacher_id"]
        verbose_name = "Teacher / Staff"
        verbose_name_plural = "Teachers & Staff"

    def __str__(self):
        return f"{self.teacher_id} - {self.full_name} ({self.designation})"

    def get_absolute_url(self):
        return reverse("teacher_detail", kwargs={"pk": self.pk})


class MonthlySalaryBill(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="salary_bills"
    )
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()  # e.g. 2026
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    days_present = models.IntegerField(default=30)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    voucher_no = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ("teacher", "month", "year")
        ordering = ["-year", "-month"]
        verbose_name = "Monthly Salary Bill"
        verbose_name_plural = "Monthly Salary Bills"

    def __str__(self):
        return f"{self.teacher.full_name} - {self.month_name} {self.year} (Net: {self.net_payable})"

    @property
    def month_name(self):
        import calendar
        try:
            return calendar.month_name[int(self.month)]
        except (IndexError, TypeError, ValueError):
            return f"Month {self.month}"

    @property
    def month_abbr(self):
        import calendar
        try:
            return calendar.month_abbr[int(self.month)]
        except (IndexError, TypeError, ValueError):
            return str(self.month)

    @property
    def period_display(self):
        return f"{self.month_name} {self.year}"

    @property
    def gross_pay(self):
        return (self.base_pay or Decimal("0.00")) + (self.allowances or Decimal("0.00"))

    @property
    def absent_days(self):
        return max(0, 30 - int(self.days_present or 30))

    @property
    def daily_rate(self):
        if self.base_pay and self.base_pay > 0:
            return (self.base_pay / Decimal("30.0")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def auto_absent_deduction(self):
        if self.base_pay and self.base_pay > 0 and self.absent_days > 0:
            daily_rate = self.base_pay / Decimal("30.0")
            return (Decimal(str(self.absent_days)) * daily_rate).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def other_deductions(self):
        return max(Decimal("0.00"), (self.deductions or Decimal("0.00")) - self.auto_absent_deduction)

    @property
    def net_payable(self):
        return max(Decimal("0.00"), self.gross_pay - (self.deductions or Decimal("0.00")))

    @property
    def actual_paid(self):
        if self.paid_amount and self.paid_amount > 0:
            return self.paid_amount
        if self.is_paid:
            return self.net_payable
        return Decimal("0.00")

    @property
    def balance_left(self):
        return max(Decimal("0.00"), self.net_payable - self.actual_paid)

    @property
    def payment_status(self):
        if self.actual_paid >= self.net_payable and self.net_payable > 0:
            return "Cleared"
        elif self.actual_paid > 0:
            return "Partial"
        return "Pending"

    def save(self, *args, **kwargs):
        if self.is_paid and (not self.paid_amount or self.paid_amount == 0):
            self.paid_amount = self.net_payable
        if self.paid_amount and self.paid_amount >= self.net_payable and self.net_payable > 0:
            self.is_paid = True
        elif self.paid_amount and self.paid_amount < self.net_payable:
            self.is_paid = False
        if self.is_paid and not self.payment_date:
            self.payment_date = timezone.now().date()
        super().save(*args, **kwargs)
