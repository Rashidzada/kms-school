from datetime import datetime, time
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

    def get_qr_code_base64(self):
        """
        Generate base64-encoded crisp pure black/white PNG QR Code for fast scanning.
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
            qr.add_data(str(self.teacher_id))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception:
            return ""



def _parse_time_val(val, default_val=None):
    from datetime import time as dt_time, datetime as dt_datetime
    if isinstance(val, dt_time):
        return val
    if isinstance(val, str) and val.strip():
        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M%p"):
            try:
                return dt_datetime.strptime(val.strip(), fmt).time()
            except ValueError:
                pass
    return default_val


class TeacherAttendanceSetting(models.Model):
    shift_start_time = models.TimeField(
        default=time(8, 0),
        help_text="Official shift start time (e.g. 08:00 AM)",
    )
    shift_end_time = models.TimeField(
        default=time(12, 30),
        help_text="Official shift end time (e.g. 12:30 PM)",
    )
    grace_period_minutes = models.IntegerField(
        default=15,
        help_text="Grace minutes allowed after shift start before marked Late",
    )
    working_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("4.50"),
        help_text="Standard daily working hours (e.g. 4.50 hrs from 8am to 12:30pm)",
    )
    working_days_per_month = models.IntegerField(
        default=30,
        help_text="Standard working days per month for daily rate calculation (typically 30)",
    )
    late_deduction_type = models.CharField(
        max_length=20,
        choices=[
            ("hourly", "Hourly Pro-rata (Based on hourly salary rate)"),
            ("per_minute", "Per-minute Pro-rata (Based on minute rate)"),
            ("fixed", "Fixed Penalty per Late Arrival"),
            ("none", "No Automatic Late Deduction"),
        ],
        default="hourly",
        help_text="Late arrival deduction calculation policy",
    )
    late_fixed_penalty = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Fixed penalty amount if deduction type is Fixed",
    )
    half_day_threshold_minutes = models.IntegerField(
        default=120,
        help_text="Arrival delay exceeding this (in minutes) counts as Half Day",
    )

    class Meta:
        verbose_name = "Teacher Attendance Setting"
        verbose_name_plural = "Teacher Attendance Settings"

    def __str__(self):
        st = _parse_time_val(self.shift_start_time, time(8, 0))
        et = _parse_time_val(self.shift_end_time, time(12, 30))
        return f"Shift: {st.strftime('%I:%M %p')} - {et.strftime('%I:%M %p')}"

    @classmethod
    def get_settings(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj


class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Late", "Late Comer"),
        ("Half Day", "Half Day"),
        ("Absent", "Absent"),
        ("Leave", "Approved Leave (PTO)"),
        ("Holiday", "Holiday / Off Day"),
    ]

    METHOD_CHOICES = [
        ("QR Code", "QR Code Scan"),
        ("Manual", "Manual Register"),
        ("Fingerprint", "Fingerprint / Biometric"),
    ]

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Present")
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    attendance_method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default="QR Code"
    )
    late_minutes = models.IntegerField(default=0)
    early_leave_minutes = models.IntegerField(default=0)
    working_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.00")
    )
    deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Salary cut amount for this day (PKR)",
    )
    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Daily bonus / incentive reward (PKR)",
    )
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("teacher", "date")
        ordering = ["-date", "teacher__teacher_id"]
        verbose_name = "Teacher Attendance"
        verbose_name_plural = "Teacher Attendances"

    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} ({self.status})"

    def calculate_and_apply_deduction(self, setting=None):
        """
        Calculate daily rate, hourly rate, late penalty or absent cutting according
        to Kohisar Model School policy.
        """
        if not setting:
            setting = TeacherAttendanceSetting.get_settings()

        base_pay = Decimal("0.00")
        if self.teacher.salary_scale and self.teacher.salary_scale.basic_pay:
            base_pay = self.teacher.salary_scale.basic_pay

        working_days = Decimal(str(setting.working_days_per_month or 30))
        daily_rate = (base_pay / working_days).quantize(Decimal("0.01")) if base_pay > 0 else Decimal("0.00")

        working_hrs = Decimal(str(setting.working_hours_per_day or 4.5))
        if working_hrs <= 0:
            working_hrs = Decimal("4.5")
        hourly_rate = (daily_rate / working_hrs).quantize(Decimal("0.01")) if daily_rate > 0 else Decimal("0.00")
        minute_rate = (hourly_rate / Decimal("60.0")).quantize(Decimal("0.0001")) if hourly_rate > 0 else Decimal("0.00")

        if self.status == "Absent":
            self.deduction_amount = daily_rate
            self.late_minutes = 0
            return

        if self.status in ("Leave", "Holiday"):
            self.deduction_amount = Decimal("0.00")
            self.late_minutes = 0
            return

        shift_start = _parse_time_val(setting.shift_start_time, time(8, 0))
        shift_end = _parse_time_val(setting.shift_end_time, time(12, 30))
        in_t = _parse_time_val(self.check_in)
        out_t = _parse_time_val(self.check_out)

        if in_t and shift_start:
            in_m = in_t.hour * 60 + in_t.minute
            shift_m = shift_start.hour * 60 + shift_start.minute
            diff = in_m - shift_m
            if diff > setting.grace_period_minutes:
                self.late_minutes = diff
                if diff >= setting.half_day_threshold_minutes:
                    self.status = "Half Day"
                else:
                    self.status = "Late"
            else:
                self.late_minutes = 0
                if self.status not in ("Half Day",):
                    self.status = "Present"

        if in_t and out_t:
            in_m = in_t.hour * 60 + in_t.minute
            out_m = out_t.hour * 60 + out_t.minute
            total_m = max(0, out_m - in_m)
            self.working_hours = (Decimal(str(total_m)) / Decimal("60.0")).quantize(Decimal("0.01"))

            shift_end_m = shift_end.hour * 60 + shift_end.minute
            if out_m < shift_end_m:
                self.early_leave_minutes = max(0, shift_end_m - out_m)
            else:
                self.early_leave_minutes = 0

        if self.status == "Half Day":
            self.deduction_amount = (daily_rate / Decimal("2.0")).quantize(Decimal("0.01"))
        elif self.status == "Late":
            if setting.late_deduction_type == "hourly":
                hours_late = Decimal(str(self.late_minutes)) / Decimal("60.0")
                self.deduction_amount = (hours_late * hourly_rate).quantize(Decimal("0.01"))
            elif setting.late_deduction_type == "per_minute":
                self.deduction_amount = (Decimal(str(self.late_minutes)) * minute_rate).quantize(Decimal("0.01"))
            elif setting.late_deduction_type == "fixed":
                self.deduction_amount = setting.late_fixed_penalty
            else:
                self.deduction_amount = Decimal("0.00")
        elif self.status == "Present":
            self.deduction_amount = Decimal("0.00")


class TeacherLoan(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active / Ongoing"),
        ("Cleared", "Fully Repaid / Cleared"),
    ]

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="loans"
    )
    loan_title = models.CharField(
        max_length=200, default="Staff Personal Loan / Advance"
    )
    loan_date = models.DateField(default=timezone.now)
    principal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total loan/advance amount approved (PKR)"
    )
    monthly_installment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Standard monthly installment to deduct from salary (PKR)",
    )
    total_repaid = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    is_cleared = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-loan_date", "-id"]
        verbose_name = "Teacher Loan / Advance"
        verbose_name_plural = "Teacher Loans & Advances"

    def __str__(self):
        return f"{self.teacher.full_name} - {self.loan_title} (Bal: PKR {self.remaining_balance:,.2f})"

    @property
    def remaining_balance(self):
        bal = (self.principal_amount or Decimal("0.00")) - (self.total_repaid or Decimal("0.00"))
        return max(Decimal("0.00"), bal)

    def save(self, *args, **kwargs):
        if self.remaining_balance <= 0 and (self.principal_amount or Decimal("0.00")) > 0:
            self.is_cleared = True
            self.status = "Cleared"
        else:
            self.is_cleared = False
            self.status = "Active"
        super().save(*args, **kwargs)


class TeacherLoanRepayment(models.Model):
    loan = models.ForeignKey(
        TeacherLoan, on_delete=models.CASCADE, related_name="repayments"
    )
    salary_bill = models.ForeignKey(
        "MonthlySalaryBill",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_repayments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("Salary Deduction", "Salary Deduction"),
            ("Cash", "Direct Cash"),
            ("Bank Transfer", "Bank Transfer"),
        ],
        default="Salary Deduction",
    )
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-id"]
        verbose_name = "Loan Repayment"
        verbose_name_plural = "Loan Repayments"

    def __str__(self):
        return f"Repayment PKR {self.amount} for {self.loan.teacher.full_name} ({self.payment_date})"


class MonthlySalaryBill(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="salary_bills"
    )
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()  # e.g. 2026
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    days_present = models.IntegerField(default=30)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    late_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    absent_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    days_late = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    days_half_day = models.IntegerField(default=0)
    days_leave = models.IntegerField(default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    voucher_no = models.CharField(max_length=50, blank=True)

    # KMS Teacher Loan & Previous Month Dues Carry-over Features
    deduct_loan = models.BooleanField(
        default=False,
        help_text="Custom option: Deduct loan/advance installment from this salary?",
    )
    loan_deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Specific loan installment amount deducted in this slip",
    )
    previous_unpaid_dues = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Old unpaid salary dues carried over from prior months (e.g. Jan + Feb unpaid)",
    )

    class Meta:
        unique_together = ("teacher", "month", "year")
        ordering = ["-year", "-month"]
        verbose_name = "Monthly Salary Bill"
        verbose_name_plural = "Monthly Salary Bills"

    def __str__(self):
        return f"{self.teacher.full_name} - {self.month_name} {self.year} (Final Net: {self.final_net_payable})"

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
        return (self.base_pay or Decimal("0.00")) + (self.allowances or Decimal("0.00")) + (self.bonus or Decimal("0.00"))

    @property
    def absent_days(self):
        if self.days_absent > 0:
            return self.days_absent
        return max(0, 30 - int(self.days_present or 30))

    @property
    def daily_rate(self):
        if self.base_pay and self.base_pay > 0:
            return (self.base_pay / Decimal("30.0")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def auto_absent_deduction(self):
        if self.absent_deductions and self.absent_deductions > 0:
            return self.absent_deductions
        if self.base_pay and self.base_pay > 0 and self.absent_days > 0:
            daily_rate = self.base_pay / Decimal("30.0")
            return (Decimal(str(self.absent_days)) * daily_rate).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def other_deductions(self):
        calculated = (self.absent_deductions or self.auto_absent_deduction) + (self.late_deductions or Decimal("0.00"))
        return max(Decimal("0.00"), (self.deductions or Decimal("0.00")) - calculated)

    @property
    def current_month_net_payable(self):
        """Current month net salary before adding old dues or deducting loans."""
        return max(Decimal("0.00"), self.gross_pay - (self.deductions or Decimal("0.00")))

    @property
    def net_payable(self):
        """Legacy property pointing to final_net_payable."""
        return self.final_net_payable

    @property
    def actual_paid(self):
        if self.paid_amount and self.paid_amount > 0:
            return self.paid_amount
        if self.is_paid:
            return self.final_net_payable
        return Decimal("0.00")

    @property
    def balance_left(self):
        return max(Decimal("0.00"), self.final_net_payable - self.actual_paid)

    @property
    def payment_status(self):
        if self.actual_paid >= self.final_net_payable and self.final_net_payable > 0:
            return "Cleared"
        elif self.actual_paid > 0:
            return "Partial"
        return "Pending"

    def get_unpaid_previous_bills(self):
        """
        Retrieves all previous months' salary bills for this teacher that were either
        unpaid or partially paid (e.g. Jan + Feb if he/she didn't take salary).
        """
        from django.db.models import Q
        prior_bills = MonthlySalaryBill.objects.filter(
            teacher=self.teacher
        ).filter(
            Q(year__lt=self.year) | Q(year=self.year, month__lt=self.month)
        ).order_by("year", "month")

        unpaid_list = []
        for pb in prior_bills:
            curr_net = max(Decimal("0.00"), pb.gross_pay - (pb.deductions or Decimal("0.00")))
            unpaid_bal = max(Decimal("0.00"), curr_net - (pb.paid_amount or Decimal("0.00")))
            if unpaid_bal > Decimal("0.00") and not pb.is_paid:
                unpaid_list.append({
                    "bill": pb,
                    "month": pb.month,
                    "year": pb.year,
                    "period": pb.period_display,
                    "gross_pay": pb.gross_pay,
                    "deductions": pb.deductions,
                    "net_payable": curr_net,
                    "paid_amount": pb.paid_amount or Decimal("0.00"),
                    "unpaid_amount": unpaid_bal,
                })
        return unpaid_list

    @property
    def calculated_previous_dues(self):
        """Sum of unpaid balances across all prior months."""
        unpaid_bills = self.get_unpaid_previous_bills()
        return sum(item["unpaid_amount"] for item in unpaid_bills)

    @property
    def effective_previous_dues(self):
        """Returns explicitly set previous_unpaid_dues or auto-calculated unpaid months dues."""
        if self.previous_unpaid_dues > 0:
            return self.previous_unpaid_dues
        return self.calculated_previous_dues

    def get_active_loans(self):
        """Active loans from school for this teacher."""
        return TeacherLoan.objects.filter(teacher=self.teacher, is_cleared=False)

    @property
    def total_outstanding_loan(self):
        """Total remaining loan balance of the teacher from the school."""
        return sum(loan.remaining_balance for loan in self.get_active_loans())

    @property
    def effective_loan_deduction(self):
        """If deduct_loan custom option is ON, return loan_deduction_amount, else 0.00."""
        if self.deduct_loan and self.loan_deduction_amount > 0:
            return min(self.loan_deduction_amount, self.total_outstanding_loan or self.loan_deduction_amount)
        return Decimal("0.00")

    @property
    def total_gross_payable(self):
        """Current month gross + any previous months unpaid dues."""
        return self.gross_pay + self.effective_previous_dues

    @property
    def total_all_deductions(self):
        """Regular deductions (late/absent) + loan deduction installment."""
        return (self.deductions or Decimal("0.00")) + self.effective_loan_deduction

    @property
    def final_net_payable(self):
        """
        Full Balance Sheet Net Payable:
        (Current Month Gross + Old Unpaid Dues) - (Attendance Deductions + Loan Deduction)
        """
        total = self.total_gross_payable - self.total_all_deductions
        return max(Decimal("0.00"), total)

    def sync_from_attendance(self):
        """
        Sync attendance counts, late deductions, absent cuts, and bonuses
        from TeacherAttendance for this month and year.
        """
        records = TeacherAttendance.objects.filter(
            teacher=self.teacher,
            date__year=self.year,
            date__month=self.month,
        )
        if not records.exists():
            return False

        p_count = records.filter(status="Present").count()
        l_count = records.filter(status="Late").count()
        hd_count = records.filter(status="Half Day").count()
        a_count = records.filter(status="Absent").count()
        lv_count = records.filter(status="Leave").count()

        total_present = p_count + l_count + lv_count + (hd_count * Decimal("0.5"))
        self.days_present = int(round(total_present))
        self.days_late = l_count
        self.days_absent = a_count
        self.days_half_day = hd_count
        self.days_leave = lv_count

        total_late_ded = sum(r.deduction_amount for r in records if r.status == "Late")
        total_absent_ded = sum(r.deduction_amount for r in records if r.status in ("Absent", "Half Day"))
        total_bonus = sum(r.bonus_amount for r in records)

        self.late_deductions = total_late_ded
        self.absent_deductions = total_absent_ded
        self.bonus = total_bonus
        self.deductions = total_late_ded + total_absent_ded

        # Auto-compute previous unpaid dues if not manually set
        if not self.previous_unpaid_dues or self.previous_unpaid_dues == 0:
            self.previous_unpaid_dues = self.calculated_previous_dues

        self.save()
        return True

    def save(self, *args, **kwargs):
        # Auto-populate previous dues if zero on creation
        if not self.id and (not self.previous_unpaid_dues or self.previous_unpaid_dues == 0):
            try:
                self.previous_unpaid_dues = self.calculated_previous_dues
            except Exception:
                pass

        if self.is_paid and (not self.paid_amount or self.paid_amount == 0):
            self.paid_amount = self.final_net_payable
        if self.paid_amount and self.paid_amount >= self.final_net_payable and self.final_net_payable > 0:
            self.is_paid = True
        elif self.paid_amount and self.paid_amount < self.final_net_payable:
            self.is_paid = False
        if self.is_paid and not self.payment_date:
            self.payment_date = timezone.now().date()
        super().save(*args, **kwargs)
