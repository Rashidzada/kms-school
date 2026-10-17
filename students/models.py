from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone


class FamilyHousehold(models.Model):
    family_id = models.CharField(max_length=20, unique=True, blank=True)
    father_guardian_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()

    class Meta:
        ordering = ["family_id"]
        verbose_name = "Family / Household"
        verbose_name_plural = "Families / Households"

    def __str__(self):
        return f"{self.family_id} - {self.father_guardian_name}"

    def save(self, *args, **kwargs):
        if not self.family_id:
            # Auto-generated on save: FAM-0001, FAM-0002 ... collision-checked
            last_family = FamilyHousehold.objects.order_by("-id").first()
            next_num = (last_family.id + 1) if last_family else 1
            while True:
                candidate = f"FAM-{next_num:04d}"
                if not FamilyHousehold.objects.filter(family_id=candidate).exists():
                    self.family_id = candidate
                    break
                next_num += 1
        super().save(*args, **kwargs)


class Student(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Withdrawn", "Withdrawn"),
    ]

    admission_no = models.CharField(max_length=50, blank=True, default="")
    admission_date = models.DateField(default=timezone.now)
    full_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, blank=True, default="")
    dob = models.DateField(null=True, blank=True, default=timezone.now)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    tribe_caste = models.CharField(max_length=100, blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    residence = models.TextField(blank=True, default="")
    contact_number = models.CharField(max_length=20, blank=True, default="")
    profile_picture = models.ImageField(upload_to="students/", blank=True, null=True)

    current_class = models.ForeignKey(
        "school.ClassLevel", on_delete=models.PROTECT, related_name="students"
    )
    current_section = models.ForeignKey(
        "school.Section", on_delete=models.PROTECT, related_name="students"
    )
    family = models.ForeignKey(
        FamilyHousehold,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Active")
    inactive_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    withdrawal_date = models.DateField(null=True, blank=True)
    class_at_withdrawal = models.CharField(max_length=50, blank=True)
    arrears_at_withdrawal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    # Custom / Free Fee per Student (Overrides fixed class monthly fee)
    custom_monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom monthly tuition fee for this student (PKR). Leave empty to use Class default. Enter 0 for Free / Scholarship.",
    )
    is_fee_free = models.BooleanField(
        default=False,
        help_text="Check if this student is 100% Free / Full Scholarship concession.",
    )

    class Meta:
        ordering = ["admission_no"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def effective_monthly_fee(self):
        from decimal import Decimal
        if self.is_fee_free:
            return Decimal("0.00")
        if self.custom_monthly_fee is not None:
            return self.custom_monthly_fee
        if self.current_class and self.current_class.monthly_fee is not None:
            return self.current_class.monthly_fee
        return Decimal("0.00")

    @property
    def fee_status_display(self):
        from decimal import Decimal
        if self.is_fee_free or (self.custom_monthly_fee is not None and self.custom_monthly_fee == Decimal("0.00")):
            return "100% Free / Scholarship"
        if self.custom_monthly_fee is not None:
            return f"Custom Fee: PKR {self.custom_monthly_fee:,.0f}"
        if self.current_class:
            return f"Class Fee: PKR {self.current_class.monthly_fee:,.0f}"
        return "Standard Fee"

    def __str__(self):
        return f"{self.admission_no} - {self.full_name}"

    def get_absolute_url(self):
        return reverse("student_detail", kwargs={"pk": self.pk})

    @property
    def age_years(self):
        if not self.dob:
            return None
        today = timezone.now().date()
        years = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            years -= 1
        return max(0, years)

    @property
    def age_display(self):
        if not self.dob:
            return "N/A"
        today = timezone.now().date()
        years = today.year - self.dob.year
        months = today.month - self.dob.month
        if today.day < self.dob.day:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        if years <= 0:
            return f"{max(0, months)} Mos"
        if months == 0:
            return f"{years} Yrs"
        return f"{years} Yrs {months} M"

    def get_qr_code_base64(self):
        """
        Generate base64-encoded crisp pure black/white PNG QR Code for fast student scanning.
        """
        try:
            import qrcode
            import io
            import base64
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=3,
            )
            # Use admission_no for quick lookup
            qr.add_data(str(self.admission_no or self.id))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception:
            return ""

    def save(self, *args, **kwargs):
        if not self.admission_no:
            # Auto-numbering: highest existing numeric admission_no + 1, starting at 1001
            existing_numbers = []
            for s in Student.objects.values_list("admission_no", flat=True):
                if s and s.isdigit():
                    existing_numbers.append(int(s))
            next_num = max(existing_numbers) + 1 if existing_numbers else 1001
            self.admission_no = str(next_num)
        super().save(*args, **kwargs)


class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Late", "Late Comer"),
        ("Absent", "Absent"),
        ("Leave", "Approved Leave"),
        ("Holiday", "Holiday / School Off"),
    ]

    METHOD_CHOICES = [
        ("QR Code", "QR Code Scan"),
        ("Manual", "Manual Register"),
        ("Biometric", "Biometric / RFID"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Present")
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    attendance_method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default="QR Code"
    )
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date", "student__admission_no"]
        verbose_name = "Student Attendance"
        verbose_name_plural = "Student Attendances"

    def __str__(self):
        return f"{self.student.admission_no} - {self.student.full_name} ({self.date}): {self.status}"


class PromotionHistory(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="promotions"
    )
    from_class = models.ForeignKey(
        "school.ClassLevel", on_delete=models.PROTECT, related_name="promotions_from"
    )
    to_class = models.ForeignKey(
        "school.ClassLevel", on_delete=models.PROTECT, related_name="promotions_to"
    )
    from_section = models.ForeignKey(
        "school.Section", on_delete=models.PROTECT, related_name="promotions_from"
    )
    to_section = models.ForeignKey(
        "school.Section", on_delete=models.PROTECT, related_name="promotions_to"
    )
    session = models.CharField(max_length=20)
    promotion_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-promotion_date"]
        verbose_name = "Promotion History"
        verbose_name_plural = "Promotion Histories"

    def __str__(self):
        return f"{self.student.full_name} ({self.from_class} -> {self.to_class}) on {self.promotion_date}"
