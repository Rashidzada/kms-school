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
    dob = models.DateField()
    qualification = models.TextField()
    experience = models.TextField()
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
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
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    voucher_no = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ("teacher", "month", "year")
        ordering = ["-year", "-month"]
        verbose_name = "Monthly Salary Bill"
        verbose_name_plural = "Monthly Salary Bills"

    def __str__(self):
        return f"{self.teacher.full_name} - {self.month}/{self.year} (Net: {self.net_payable})"

    @property
    def net_payable(self):
        return (self.base_pay + self.allowances) - self.deductions

    def save(self, *args, **kwargs):
        if self.is_paid and not self.payment_date:
            self.payment_date = timezone.now().date()
        super().save(*args, **kwargs)
