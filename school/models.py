from django.db import models


class SchoolSetting(models.Model):
    name = models.CharField(max_length=255, default="Kohisar Model School & College")
    address = models.TextField(default="Qalagay, Tehsil Kabal, District Swat, Khyber Pakhtunkhwa")
    logo = models.ImageField(upload_to="school_logos/", blank=True, null=True)
    contact = models.CharField(max_length=100, default="+92 344 9631323 / +92 345 3407095")
    academic_session_format = models.CharField(max_length=50, default="2025-2026")
    receipt_no_prefix = models.CharField(max_length=10, default="REC-")
    last_receipt_no = models.IntegerField(default=1000)

    class Meta:
        verbose_name = "School Setting"
        verbose_name_plural = "School Settings"

    def __str__(self):
        return self.name


class AcademicSession(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Academic Session"
        verbose_name_plural = "Academic Sessions"

    def __str__(self):
        return self.name


class ClassLevel(models.Model):
    LEVEL_CHOICES = [
        ("Prep", "Prep"),
        ("KG", "KG"),
        ("Primary", "Primary(1-5)"),
        ("Middle", "Middle(6-8)"),
        ("High", "High(9-10)"),
        ("Higher Secondary", "Higher Secondary(11-12)"),
    ]

    name = models.CharField(max_length=50, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["name"]
        verbose_name = "Class Level"
        verbose_name_plural = "Class Levels"

    def __str__(self):
        return self.name


class Section(models.Model):
    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=10)
    class_teacher = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("class_level", "name")
        ordering = ["class_level", "name"]
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"
