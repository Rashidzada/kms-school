from django.db import models
from django.utils import timezone


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Stationery", "Stationery"),
        ("Maintenance", "Maintenance"),
        ("Electricity", "Electricity"),
        ("Salary", "Salary"),
        ("Other", "Other"),
    ]
    PAYMENT_MODE_CHOICES = [
        ("Cash", "Cash"),
        ("Bank", "Bank"),
    ]

    date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    reference = models.CharField(max_length=50, blank=True)
    payment_mode = models.CharField(
        max_length=20, choices=PAYMENT_MODE_CHOICES, default="Cash"
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.date} - {self.category} ({self.amount})"
