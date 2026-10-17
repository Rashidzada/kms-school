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

    # Automated Daily Cloud Email Backup Settings (.sql + Master .xlsx)
    auto_backup_enabled = models.BooleanField(
        default=True,
        help_text="Automatically trigger daily full backup (after 1 day) with Splash Screen & Network Check",
    )
    auto_backup_interval_days = models.IntegerField(
        default=1,
        help_text="Interval in days for automatic backup (Default: 1 Day / 24 Hours)",
    )
    default_backup_email = models.EmailField(
        blank=True,
        default="",
        help_text="Optional Default Receiver Email to always receive Full .sql & .xlsx Backups",
    )
    backup_send_sql = models.BooleanField(
        default=True,
        help_text="Send Full PostgreSQL Database Dump (.sql) attachment in backup emails",
    )
    backup_send_excel = models.BooleanField(
        default=True,
        help_text="Send Full Master Excel Workbook (.xlsx) attachment in backup emails",
    )
    last_auto_backup_at = models.DateTimeField(null=True, blank=True)
    last_auto_backup_status = models.CharField(max_length=50, blank=True, default="Pending")
    last_auto_backup_message = models.TextField(blank=True, default="")

    safe_backup_folder = models.CharField(
        max_length=255,
        default="D:\\School_Backups",
        blank=True,
        null=True,
        help_text="Safe offline backup directory on hard drive (e.g. D:\\School_Backups or E:\\KMS_Backups) for auto storage",
    )
    auto_backup_mode = models.CharField(
        max_length=30,
        default="background",
        blank=True,
        null=True,
        choices=[
            ("background", "Run Silently in Background (Recommended - No Screen Popup)"),
            ("prompt", "Prompt Me First (Ask Confirmation on Due Time)"),
            ("splash", "Show Progress Splash Modal"),
        ],
        help_text="How the system handles scheduled auto backup when due",
    )
    auto_backup_preferred_time = models.TimeField(
        null=True,
        blank=True,
        default="14:00:00",
        help_text="Scheduled daily time to run/prompt backup (e.g. 14:00 for 02:00 PM)",
    )

    short_name = models.CharField(
        max_length=50,
        default="KMS",
        blank=True,
        null=True,
        help_text="Short school code / abbreviation (e.g. KMS, BPS, APS) shown in headers, tabs, badges",
    )
    tagline = models.CharField(
        max_length=150,
        default="Student Information, Fee & Payroll Management System",
        blank=True,
        null=True,
        help_text="Portal tagline / subtitle displayed in sidebar and reports",
    )
    email_provider = models.CharField(
        max_length=20,
        default="gmail_smtp",
        blank=True,
        null=True,
        choices=[
            ("gmail_smtp", "Standard Gmail SMTP (Ports 465 / 587)"),
            ("https_api", "Cloud HTTPS Email (Port 443 - Bypasses ISP/Firewall Blocks)"),
        ],
        help_text="Choose standard Gmail SMTP or Cloud HTTPS Mail API if your ISP blocks SMTP ports",
    )
    https_api_provider = models.CharField(
        max_length=20,
        default="resend",
        choices=[
            ("resend", "Resend API (api.resend.com)"),
            ("brevo", "Brevo / Sendinblue API (api.brevo.com)"),
        ],
        blank=True,
        null=True,
    )
    https_api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="",
        help_text="API Key for Resend or Brevo (Sends backup directly over HTTPS port 443)",
    )

    class Meta:
        verbose_name = "School Setting"
        verbose_name_plural = "School Settings"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-sync uploaded logo to static assets so every hardcoded and cached asset updates immediately
        if self.logo:
            try:
                from PIL import Image
                from django.conf import settings
                import os
                
                logo_src_path = self.logo.path
                if os.path.exists(logo_src_path):
                    with Image.open(logo_src_path) as img:
                        # Convert RGBA if needed
                        img_converted = img.convert("RGBA") if img.mode in ("RGBA", "LA") else img.convert("RGB")
                        
                        # 1. Update static/dist/img/logo.png
                        dist_img_dir = os.path.join(settings.BASE_DIR, "static", "dist", "img")
                        os.makedirs(dist_img_dir, exist_ok=True)
                        dest_logo = os.path.join(dist_img_dir, "logo.png")
                        img.save(dest_logo)
                        
                        # 2. Update favicon.png
                        dest_fav_png = os.path.join(dist_img_dir, "favicon.png")
                        fav_img = img_converted.resize((64, 64), Image.Resampling.LANCZOS)
                        fav_img.save(dest_fav_png, format="PNG")
                        
                        # 3. Update favicon.ico
                        dest_fav_ico = os.path.join(dist_img_dir, "favicon.ico")
                        fav_ico_img = img_converted.resize((32, 32), Image.Resampling.LANCZOS)
                        fav_ico_img.save(dest_fav_ico, format="ICO")
            except Exception:
                pass


class BackupEmailAccount(models.Model):
    """
    Email & App Password Table for Automated & Manual Cloud Backups (.sql + .xlsx).
    Supports 3 (or more) configurable Email Accounts where the admin provides only:
      1. Email Address
      2. App Password (16-digit Gmail App Password for sending)
      3. Checkboxes for whether this email Can Send and/or Should Receive the backup data.
    """
    slot_number = models.IntegerField(default=1, help_text="Account Slot (1, 2, 3)")
    account_label = models.CharField(
        max_length=100,
        blank=True,
        default="Backup Email Account",
        help_text="Friendly label (e.g. Option 1 - Primary Admin, Option 2 - Principal, Option 3 - Developer/Backup)",
    )
    email = models.EmailField(
        blank=True,
        default="",
        verbose_name="Email Address (Gmail)",
        help_text="Enter Gmail address (e.g. yourschool@gmail.com)",
    )
    app_password = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="App Password (16-char)",
        help_text="Enter 16-letter Google App Password (only required if this email sends backups)",
    )
    use_as_sender = models.BooleanField(
        default=True,
        verbose_name="Use to Send Backup?",
        help_text="If checked and App Password is provided, system can use this account to send backup emails",
    )
    receive_backup = models.BooleanField(
        default=True,
        verbose_name="Receive Backup Data (.sql & .xlsx)?",
        help_text="Check this box if this email address should receive the Full SQL & Excel backup files",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["slot_number", "id"]
        verbose_name = "Backup Email & App Password Account"
        verbose_name_plural = "Backup Email & App Password Accounts (3 Options)"

    def __str__(self):
        email_str = self.email if self.email else "Not Configured"
        roles = []
        if self.use_as_sender and self.app_password:
            roles.append("Sender")
        if self.receive_backup:
            roles.append("Receiver")
        role_str = "/".join(roles) if roles else "Inactive"
        return f"Option {self.slot_number}: {email_str} ({role_str})"

    @classmethod
    def ensure_three_slots(cls):
        defaults = [
            (1, "Option 1 - Primary School / Admin Email"),
            (2, "Option 2 - Principal / Secondary Email"),
            (3, "Option 3 - Backup / Cloud Archive Email"),
        ]
        accounts = []
        for slot, label in defaults:
            obj = cls.objects.filter(slot_number=slot).first()
            if not obj:
                obj = cls.objects.create(
                    slot_number=slot,
                    account_label=label,
                    use_as_sender=True,
                    receive_backup=True,
                    is_active=True,
                )
            accounts.append(obj)
        return accounts


class BackupHistoryLog(models.Model):
    """
    Stores history of automated daily backups, manual email backups, and database restores.
    """
    backup_type = models.CharField(
        max_length=50,
        default="Auto Daily Email Backup",
        help_text="e.g. Auto Daily Email Backup, Manual Email Backup, SQL Download, Full Restore",
    )
    status = models.CharField(
        max_length=30,
        default="Success",
        choices=[("Success", "Success"), ("Failed", "Failed"), ("Offline", "Skipped - Offline")],
    )
    sender_email = models.CharField(max_length=150, blank=True, default="")
    recipient_emails = models.TextField(blank=True, default="")
    sql_filename = models.CharField(max_length=255, blank=True, default="")
    excel_filename = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Backup & Restore Log"
        verbose_name_plural = "Backup & Restore Logs"

    def __str__(self):
        return f"{self.backup_type} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


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
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_sections",
        help_text="Select Class / Section Teacher from Staff Directory (optional)",
    )

    class Meta:
        unique_together = ("class_level", "name")
        ordering = ["class_level", "name"]
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"

    def save(self, *args, **kwargs):
        if self.teacher and not self.class_teacher:
            self.class_teacher = self.teacher.full_name
        super().save(*args, **kwargs)


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


class TimetablePeriod(models.Model):
    """
    Standard school periods: Period 01, 02, 03, 04, 05, Break / Recess, 06, 07, 08.
    """
    period_number = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=50, default="Period 1")
    start_time = models.CharField(max_length=30, blank=True, default="")
    end_time = models.CharField(max_length=30, blank=True, default="")
    is_break = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order", "period_number"]
        verbose_name = "Timetable Period"
        verbose_name_plural = "Timetable Periods"

    def __str__(self):
        return f"{self.name}"


class TimetableEntry(models.Model):
    """
    Assigned class period schedule linking ClassLevel, Period, Subject and Teacher.
    Supports conflict detection (flagging if teacher is double-booked in the same period).
    """
    DAY_CHOICES = [
        ("Daily", "Daily / Regular (Mon - Sat)"),
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]
    academic_session = models.ForeignKey(
        "school.AcademicSession",
        on_delete=models.CASCADE,
        related_name="timetable_entries",
        null=True,
        blank=True,
    )
    class_level = models.ForeignKey(
        "school.ClassLevel",
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )
    section = models.ForeignKey(
        "school.Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries",
    )
    period = models.ForeignKey(
        TimetablePeriod,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    day_of_week = models.CharField(max_length=20, default="Daily", choices=DAY_CHOICES)

    subject = models.ForeignKey(
        "exams.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries",
    )
    custom_subject = models.CharField(max_length=120, blank=True, default="")

    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries",
    )
    custom_teacher = models.CharField(max_length=120, blank=True, default="")
    room_or_note = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["period__order", "class_level__id"]
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"

    def get_subject_name(self):
        if self.custom_subject and self.custom_subject.strip():
            return self.custom_subject.strip()
        if self.subject:
            return self.subject.name
        return ""

    def get_teacher_name(self):
        if self.custom_teacher and self.custom_teacher.strip():
            return self.custom_teacher.strip()
        if self.teacher:
            return self.teacher.full_name
        return ""

    def __str__(self):
        return f"{self.class_level.name} - {self.period.name}: {self.get_subject_name()} ({self.get_teacher_name()})"
