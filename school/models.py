from django.db import models


class SchoolSetting(models.Model):
    name = models.CharField(max_length=255, default="Kohisar Model School & College")
    address = models.TextField(default="Qalagay, Tehsil Kabal, District Swat, Khyber Pakhtunkhwa")
    logo = models.ImageField(upload_to="school_logos/", blank=True, null=True)
    contact = models.CharField(max_length=100, default="+92 344 9631323 / +92 345 3407095")
    academic_session_format = models.CharField(max_length=50, default="2025-2026")
    receipt_no_prefix = models.CharField(max_length=10, default="REC-")
    last_receipt_no = models.IntegerField(default=1000)
    passing_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=30.0,
        help_text="Default passing percentage for school examinations (e.g. 30%, 33%, 40%)",
    )
    passing_rule = models.CharField(
        max_length=50,
        default="overall_only",
        choices=[
            ("overall_only", "Overall Percentage Only (Pass if Total % >= Passing %)"),
            ("subject_and_overall", "Each Subject & Overall %"),
            ("subject_only", "Each Subject Must Pass"),
        ],
        help_text="Passing evaluation criteria",
    )

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
        ordering = ["id"]
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


class SoftwareLicense(models.Model):
    """
    Standard Software License & Subscription Management:
    Allows the software vendor/developer to issue time-limited trials or subscriptions
    (minutes, hours, days, months, or years) to client schools. When expired, access
    is paused to a contact & renewal screen until renewed with the Developer Master Key.
    """
    client_name = models.CharField(max_length=255, default="Kohisar Model School & College")
    license_key = models.CharField(max_length=100, blank=True, default="KMS-LIC-STD-2026")
    developer_name = models.CharField(max_length=150, default="Rashid Zada (Lead Software Engineer)")
    developer_phone = models.CharField(max_length=50, default="+92 344 9631323")
    developer_whatsapp = models.CharField(max_length=50, default="+92 344 9631323")
    developer_email = models.EmailField(blank=True, default="developer@kms.edu.pk")
    developer_master_pin = models.CharField(
        max_length=100,
        default="Rashid@9631",
        help_text="Developer Master Key required to extend or reactivate software license",
    )

    is_active = models.BooleanField(default=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="License expiration date and time")

    notes = models.TextField(blank=True, help_text="Developer private agreement terms / payment record")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Software License & Subscription"
        verbose_name_plural = "Software Licenses & Subscriptions"

    def __str__(self):
        status = "Active" if self.is_valid() else "Expired"
        return f"{self.client_name} - {status} (Expires: {self.expires_at})"

    def is_valid(self):
        from django.utils import timezone
        if not self.is_active:
            return False
        return timezone.now() <= self.expires_at

    def time_remaining_display(self):
        from django.utils import timezone
        if not self.is_valid():
            return "License Expired"
        diff = self.expires_at - timezone.now()
        total_days = diff.days
        hours = diff.seconds // 3600
        mins = (diff.seconds % 3600) // 60

        if total_days >= 365:
            years = total_days // 365
            rem_days = total_days % 365
            months = rem_days // 30
            if months > 0:
                return f"{years} Yr{'s' if years > 1 else ''}, {months} Mo{'s' if months > 1 else ''} left"
            return f"{years} Year{'s' if years > 1 else ''} left"
        elif total_days >= 30:
            months = total_days // 30
            rem_days = total_days % 30
            if rem_days > 0:
                return f"{months} Month{'s' if months > 1 else ''}, {rem_days} Day{'s' if rem_days > 1 else ''} left"
            return f"{months} Month{'s' if months > 1 else ''} left"
        elif total_days >= 1:
            if hours > 0:
                return f"{total_days} Day{'s' if total_days > 1 else ''}, {hours} Hr{'s' if hours > 1 else ''} left"
            return f"{total_days} Day{'s' if total_days > 1 else ''} left"
        elif hours >= 1:
            return f"{hours} Hr{'s' if hours > 1 else ''}, {mins} Min{'s' if mins > 1 else ''} left"
        else:
            return f"{max(0, mins)} Mins left"

    @property
    def status_badge_class(self):
        from django.utils import timezone
        if not self.is_valid():
            return "bg-danger text-white"
        diff = self.expires_at - timezone.now()
        days = diff.days
        if days > 30:
            return "bg-success text-white"
        elif days > 7:
            return "bg-info text-dark"
        elif days > 1:
            return "bg-warning text-dark"
        else:
            return "bg-danger text-white"

    @classmethod
    def get_license(cls):
        from django.utils import timezone
        from datetime import timedelta
        lic = cls.objects.first()
        if not lic:
            lic = cls.objects.create(
                client_name="Kohisar Model School & College",
                license_key="KMS-LIC-MASTER-2026",
                developer_name="Rashid Zada (Lead Software Engineer)",
                developer_phone="+92 344 9631323",
                developer_whatsapp="+92 344 9631323",
                developer_master_pin="Rashid@9631",
                expires_at=timezone.now() + timedelta(days=365),
            )
        return lic
