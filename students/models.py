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

    admission_no = models.CharField(max_length=20, unique=True, blank=True)
    admission_date = models.DateField(default=timezone.now)
    full_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
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

    class Meta:
        ordering = ["admission_no"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.admission_no} - {self.full_name}"

    def get_absolute_url(self):
        return reverse("student_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.admission_no:
            # Auto-numbering: highest existing numeric admission_no + 1, starting at 1001
            existing_numbers = []
            for s in Student.objects.values_list("admission_no", flat=True):
                if s and s.isdigit():
                    existing_numbers.append(int(s))
            next_num = max(existing_numbers) + 1 if existing_numbers else 1001
            while Student.objects.filter(admission_no=str(next_num)).exists():
                next_num += 1
            self.admission_no = str(next_num)
        super().save(*args, **kwargs)


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
