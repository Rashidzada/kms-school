import os
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AcademicSessionForm, ClassLevelForm, SchoolSettingForm, SectionForm
from .models import AcademicSession, ClassLevel, SchoolSetting, Section


@login_required
def dashboard(request):
    """
    KMS Dashboard (FR-9.1):
    Active students count, active teachers count, current month fee collection,
    current month expenses (general + paid salaries), and 5 most recent receipts.
    """
    from accounts.models import Expense
    from finance.models import FeePaymentReceipt
    from students.models import Student
    from teachers.models import MonthlySalaryBill, Teacher

    today = timezone.now().date()
    active_students_count = Student.objects.filter(status="Active").count()
    active_teachers_count = Teacher.objects.filter(status="Active").count()

    # Total fee collected in current calendar month
    fee_collected_month = (
        FeePaymentReceipt.objects.filter(
            payment_date__year=today.year, payment_date__month=today.month
        ).aggregate(total=Sum("amount_paid"))["total"]
        or Decimal("0.00")
    )

    # Total general expenses in current month
    general_expenses_month = (
        Expense.objects.filter(
            date__year=today.year, date__month=today.month
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # Paid salary bills in current month (treated as expense per SRS rule 10)
    paid_salary_bills = MonthlySalaryBill.objects.filter(
        is_paid=True,
        payment_date__year=today.year,
        payment_date__month=today.month,
    )
    salaries_paid_month = Decimal("0.00")
    for bill in paid_salary_bills:
        salaries_paid_month += bill.net_payable

    total_expenses_month = general_expenses_month + salaries_paid_month

    # 5 most recent fee receipts
    recent_receipts = FeePaymentReceipt.objects.select_related("student").order_by(
        "-id"
    )[:5]

    context = {
        "active_students_count": active_students_count,
        "active_teachers_count": active_teachers_count,
        "fee_collected_month": fee_collected_month,
        "total_expenses_month": total_expenses_month,
        "recent_receipts": recent_receipts,
        "today": today,
    }
    return render(request, "school/dashboard.html", context)


@login_required
def download_db_backup(request):
    """
    One-click database backup (FR-9.2):
    Supports PostgreSQL (live pg_dump SQL stream) and SQLite (.sqlite3 file).
    """
    import subprocess
    from io import BytesIO
    from django.http import HttpResponse

    db_config = settings.DATABASES["default"]
    engine = db_config.get("ENGINE", "")
    timestamp = timezone.now().strftime("%Y%m%d_%H%M")

    if "postgresql" in engine:
        pg_dump_path = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
        if not os.path.exists(pg_dump_path):
            pg_dump_path = "pg_dump"

        env = os.environ.copy()
        env["PGPASSWORD"] = str(db_config.get("PASSWORD", ""))

        cmd = [
            pg_dump_path,
            "-h", str(db_config.get("HOST", "127.0.0.1")),
            "-p", str(db_config.get("PORT", "5432")),
            "-U", str(db_config.get("USER", "postgres")),
            "--no-owner",
            "--no-privileges",
            str(db_config.get("NAME", "kms_db")),
        ]
        try:
            res = subprocess.run(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
            filename = f"KMS_Backup_{timestamp}.sql"
            response = HttpResponse(res.stdout, content_type="application/sql")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception:
            # Fallback: export Django JSON dumpdata
            from django.core.management import call_command
            buf = BytesIO()
            call_command("dumpdata", stdout=buf)
            buf.seek(0)
            filename = f"KMS_Backup_{timestamp}.json"
            response = HttpResponse(buf.read(), content_type="application/json")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
    else:
        db_path = db_config["NAME"]
        if not os.path.exists(db_path):
            raise Http404("Database file not found.")
        filename = f"KMS_Backup_{timestamp}.sqlite3"
        return FileResponse(open(db_path, "rb"), as_attachment=True, filename=filename)


@login_required
def school_settings(request):
    setting = SchoolSetting.objects.first()
    if request.method == "POST":
        form = SchoolSettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "School settings successfully updated.")
            return redirect("school_settings")
    else:
        form = SchoolSettingForm(instance=setting)

    return render(request, "school/settings.html", {"form": form, "setting": setting})


@login_required
def session_list(request):
    sessions = AcademicSession.objects.all()
    if request.method == "POST":
        form = AcademicSessionForm(request.POST)
        if form.is_valid():
            new_session = form.save()
            if new_session.is_active:
                AcademicSession.objects.exclude(id=new_session.id).update(
                    is_active=False
                )
            messages.success(request, "Academic session created successfully.")
            return redirect("session_list")
    else:
        form = AcademicSessionForm()

    return render(
        request, "school/session_list.html", {"sessions": sessions, "form": form}
    )


@login_required
def class_list(request):
    classes = ClassLevel.objects.prefetch_related("sections").all()
    if request.method == "POST":
        form = ClassLevelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class level created successfully.")
            return redirect("class_list")
    else:
        form = ClassLevelForm()

    section_form = SectionForm()
    return render(
        request,
        "school/class_list.html",
        {"classes": classes, "form": form, "section_form": section_form},
    )


@login_required
def section_create(request):
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Section created successfully.")
        else:
            messages.error(request, "Error creating section. Ensure section name is unique for the class.")
    return redirect("class_list")
