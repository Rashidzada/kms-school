import os
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .excel_utils import (
    create_styled_workbook,
    excel_download_response,
    parse_excel_upload,
)

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
        salaries_paid_month += bill.actual_paid

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


@login_required
def export_classes_excel(request):
    """
    Export all Class Levels and their Sections to an Excel spreadsheet.
    """
    from students.models import Student
    classes = ClassLevel.objects.prefetch_related("sections").all()
    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Class Name",
        "Academic Level",
        "Standard Monthly Fee (PKR)",
        "Sections",
        "Total Active Students",
    ]

    rows = []
    for c in classes:
        sec_names = ", ".join([s.name for s in c.sections.all()]) or "None"
        student_count = Student.objects.filter(current_class=c, status="Active").count()
        rows.append([
            c.name,
            c.level,
            float(c.monthly_fee),
            sec_names,
            student_count,
        ])

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"Classes_Sections_{timestamp}.xlsx"
    buffer = create_styled_workbook("Classes & Sections Directory", headers, rows, school_name=school_name)
    return excel_download_response(buffer, filename)


@login_required
def download_class_template(request):
    """
    Download a pre-formatted template for bulk onboarding classes and sections.
    """
    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Class Name *",
        "Level (Prep/KG/Primary/Middle/High/Higher Secondary) *",
        "Monthly Fee (PKR) *",
        "Sections (Comma-separated, e.g. A, B, C)",
    ]

    sample_rows = [
        ["Nursery", "Prep", 1200.0, "A, B"],
        ["Prep", "Prep", 1200.0, "A, B"],
        ["KG", "KG", 1300.0, "A, B, C"],
        ["Class 1", "Primary", 1400.0, "A, B"],
        ["Class 2", "Primary", 1400.0, "A, B"],
        ["Class 3", "Primary", 1500.0, "A, B"],
        ["Class 4", "Primary", 1500.0, "A, B"],
        ["Class 5", "Primary", 1600.0, "A, B"],
        ["Class 6th", "Middle", 1700.0, "A, B"],
        ["Class 7th", "Middle", 1700.0, "A, B"],
        ["Class 8th", "Middle", 1800.0, "A, B"],
        ["Class 9th", "High", 2000.0, "Science-A, Science-B, Arts"],
        ["Class 10th", "High", 2200.0, "Science-A, Science-B, Arts"],
    ]

    buffer = create_styled_workbook("Classes Onboarding Template", headers, sample_rows, school_name=school_name)
    return excel_download_response(buffer, "KMS_Class_Import_Template.xlsx")


@login_required
def import_classes_excel(request):
    """
    Bulk import classes and sections from an uploaded Excel file.
    """
    if request.method != "POST" or "excel_file" not in request.FILES:
        messages.error(request, "Please choose a valid Excel (.xlsx) file to upload.")
        return redirect("class_list")

    excel_file = request.FILES["excel_file"]
    records, errors = parse_excel_upload(excel_file, header_row=2)

    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect("class_list")

    if not records:
        messages.warning(request, "The uploaded Excel file contains no class data rows.")
        return redirect("class_list")

    success_count = 0
    row_errors = []

    valid_levels = {
        "prep": "Prep",
        "kg": "KG",
        "primary": "Primary",
        "middle": "Middle",
        "high": "High",
        "higher secondary": "Higher Secondary",
    }

    try:
        with transaction.atomic():
            for r in records:
                row_num = r.get("_row_number", "?")
                name = str(r.get("class_name__", "") or r.get("class_name", "") or r.get("name", "")).strip()

                if not name:
                    row_errors.append(f"Row {row_num}: Missing Class Name.")
                    continue

                raw_level = str(r.get("level__prep_kg_primary_middle_high_higher_secondary___", "") or r.get("level", "Primary")).strip().lower()
                level = valid_levels.get(raw_level, "Primary")

                fee_raw = r.get("monthly_fee__pkr___", None) or r.get("monthly_fee", 0.0)
                try:
                    monthly_fee = Decimal(str(fee_raw).strip() or "0.00")
                except Exception:
                    monthly_fee = Decimal("0.00")

                class_obj, created = ClassLevel.objects.get_or_create(
                    name=name,
                    defaults={"level": level, "monthly_fee": monthly_fee},
                )
                if not created:
                    class_obj.level = level
                    class_obj.monthly_fee = monthly_fee
                    class_obj.save()

                # Create sections if provided
                sec_raw = str(r.get("sections__comma_separated__e_g__a__b__c_", "") or r.get("sections", "")).strip()
                if sec_raw:
                    section_names = [s.strip().upper() for s in sec_raw.replace(";", ",").split(",") if s.strip()]
                    for sec_name in section_names:
                        Section.objects.get_or_create(class_level=class_obj, name=sec_name)
                else:
                    Section.objects.get_or_create(class_level=class_obj, name="A")

                success_count += 1

        if success_count > 0:
            messages.success(request, f"Excel Import Completed! Successfully imported {success_count} classes and their sections.")
        if row_errors:
            messages.warning(request, f"Some rows were skipped: {'; '.join(row_errors[:5])}")
    except Exception as e:
        messages.error(request, f"Excel Import Failed: {str(e)}")

    return redirect("class_list")


@login_required
def excel_data_hub(request):
    """
    Central Data Exchange Hub:
    Allows one-stop downloading of sample templates, comprehensive Excel backups,
    and bulk imports for Students, Teachers, Classes, Accounts, and Fees.
    """
    from students.models import Student
    from teachers.models import Teacher

    active_students = Student.objects.filter(status="Active").count()
    total_students = Student.objects.count()
    active_teachers = Teacher.objects.filter(status="Active").count()
    total_classes = ClassLevel.objects.count()
    total_sections = Section.objects.count()

    context = {
        "active_students": active_students,
        "total_students": total_students,
        "active_teachers": active_teachers,
        "total_classes": total_classes,
        "total_sections": total_sections,
    }
    return render(request, "school/excel_hub.html", context)


def custom_page_not_found(request, exception=None):
    """
    Custom 404 handler for missing pages.
    """
    return render(request, "404.html", status=404)


def custom_server_error(request):
    """
    Custom 500 handler for unexpected server errors.
    """
    return render(request, "500.html", status=500)

