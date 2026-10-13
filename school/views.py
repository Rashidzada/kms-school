import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .excel_utils import (
    create_styled_workbook,
    excel_download_response,
    parse_excel_upload,
)

from .forms import AcademicSessionForm, ClassLevelForm, SchoolSettingForm, SectionForm
from .models import (
    AcademicSession,
    BackupEmailAccount,
    BackupHistoryLog,
    ClassLevel,
    SchoolSetting,
    Section,
    SoftwareLicense,
)
from .backup_utils import (
    check_network_connection,
    generate_full_master_excel,
    generate_full_sql_dump,
    restore_from_master_excel,
    restore_from_sql_bytes,
    send_backup_email_now,
    sync_all_postgresql_sequences,
)


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
    One-click Full PostgreSQL Database Backup (.sql):
    Generates a 100% complete, self-contained .sql script including ALL tables:
    Students, Teachers, Classes, Sections, Exams, Subjects, Student Exam Marks,
    Fee Ledgers, Fee Payment Receipts, Monthly Salary Bills, Loans, Attendance & Expenses.
    """
    from django.http import HttpResponse

    timestamp = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M")
    sql_bytes = generate_full_sql_dump()
    filename = f"KMS_Full_PostgreSQL_Backup_{timestamp}.sql"

    # Also save local copy in backups/ folder
    backups_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    try:
        with open(os.path.join(backups_dir, filename), "wb") as f:
            f.write(sql_bytes)
    except Exception:
        pass

    BackupHistoryLog.objects.create(
        backup_type="Full SQL Download (.sql)",
        status="Success",
        sql_filename=filename,
        details=f"Downloaded Full PostgreSQL Database Backup ({len(sql_bytes) // 1024} KB)",
    )

    response = HttpResponse(sql_bytes, content_type="application/sql; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def download_master_excel_backup(request):
    """
    One-click Full 16-Sheet Master Excel Backup (.xlsx):
    Contains Students, Teachers, Classes & Sections, Families, Exams, Subjects,
    ALL Exam Marks, Fee Ledgers, Fee Payment Receipts, Salary Bills, Loans, Expenses & Attendance.
    """
    timestamp = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M")
    filename = f"KMS_Full_Master_Backup_{timestamp}.xlsx"
    buffer = generate_full_master_excel()

    backups_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    try:
        with open(os.path.join(backups_dir, filename), "wb") as f:
            f.write(buffer.getvalue())
    except Exception:
        pass

    BackupHistoryLog.objects.create(
        backup_type="Full Master Excel Download (.xlsx)",
        status="Success",
        excel_filename=filename,
        details="Downloaded 16-Sheet Full Master Excel Backup",
    )
    buffer.seek(0)
    return excel_download_response(buffer, filename)


@login_required
def restore_full_database(request):
    """
    One-Click Full Database Restore from Web UI:
    Accepts:
      - .sql (Full PostgreSQL Backup generated by KMS or pg_dump)
      - .xlsx (Full 16-Sheet Master Excel Backup)
      - .json (Django dumpdata fixture)
    Restores ALL data (Students, Teachers, Classes, Sections, Exam Marks, Fee Receipts,
    Salary Bills, Loans, Expenses) and automatically synchronizes PostgreSQL sequences.
    """
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "school_settings"
    if request.method != "POST" or "backup_file" not in request.FILES:
        messages.error(request, "Please select a valid .sql, .xlsx, or .json backup file to restore.")
        return redirect(next_url)

    uploaded = request.FILES["backup_file"]
    fname = uploaded.name.lower()

    try:
        if fname.endswith(".sql"):
            sql_bytes = uploaded.read()
            ok, msg = restore_from_sql_bytes(sql_bytes)
            if ok:
                BackupHistoryLog.objects.create(
                    backup_type="Full SQL Restore (.sql)",
                    status="Success",
                    sql_filename=uploaded.name,
                    details=msg,
                )
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        elif fname.endswith((".xlsx", ".xls")):
            ok, msg = restore_from_master_excel(uploaded)
            if ok:
                BackupHistoryLog.objects.create(
                    backup_type="Full Master Excel Restore (.xlsx)",
                    status="Success",
                    excel_filename=uploaded.name,
                    details=msg,
                )
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        elif fname.endswith(".json"):
            import tempfile
            from django.core.management import call_command

            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                for chunk in uploaded.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            try:
                call_command("loaddata", tmp_path)
                sync_all_postgresql_sequences()
                messages.success(request, f"Successfully restored database from JSON fixture ({uploaded.name})!")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            messages.error(request, "Unsupported file format. Please upload a .sql, .xlsx, or .json backup file.")
    except Exception as e:
        messages.error(request, f"Database Restore Error: {str(e)}")

    return redirect(next_url)


@login_required
def api_check_backup_network(request):
    """
    AJAX endpoint for the Auto Daily Backup Splash Screen:
    Verifies internet & SMTP server connectivity before generating/sending backup.
    """
    online, msg = check_network_connection()
    return JsonResponse({"online": online, "message": msg})


@login_required
def api_run_email_backup(request):
    """
    AJAX endpoint for the Auto Daily Backup Splash Screen (or 1-click Send Backup Now button):
    Generates both Full .sql and Full Master .xlsx backups and emails them to all selected recipients.
    """
    is_auto = request.POST.get("is_auto") == "1" or request.GET.get("is_auto") == "1"
    ok, msg = send_backup_email_now(is_auto=is_auto)
    return JsonResponse({"success": ok, "message": msg})


@login_required
def school_settings(request):
    setting = SchoolSetting.objects.first()
    if not setting:
        setting = SchoolSetting.objects.create()

    email_accounts = BackupEmailAccount.ensure_three_slots()

    if request.method == "POST":
        action = request.POST.get("action", "save_all")

        if action == "save_email_table":
            for acc in email_accounts:
                prefix = f"acc_{acc.slot_number}_"
                acc.account_label = request.POST.get(prefix + "label", acc.account_label).strip()
                acc.email = request.POST.get(prefix + "email", "").strip()
                entered_pass = request.POST.get(prefix + "app_password", "").strip()
                if entered_pass:
                    acc.app_password = entered_pass
                elif request.POST.get(prefix + "clear_pass") == "1":
                    acc.app_password = ""
                acc.use_as_sender = request.POST.get(prefix + "use_as_sender") == "on"
                acc.receive_backup = request.POST.get(prefix + "receive_backup") == "on"
                acc.is_active = request.POST.get(prefix + "is_active") == "on"
                acc.save()

            setting.auto_backup_enabled = request.POST.get("auto_backup_enabled") == "on"
            try:
                setting.auto_backup_interval_days = max(1, int(request.POST.get("auto_backup_interval_days", 1) or 1))
            except ValueError:
                setting.auto_backup_interval_days = 1
            setting.default_backup_email = request.POST.get("default_backup_email", "").strip()
            setting.backup_send_sql = request.POST.get("backup_send_sql") == "on"
            setting.backup_send_excel = request.POST.get("backup_send_excel") == "on"
            setting.save()

            if request.POST.get("send_now") == "1":
                ok, msg = send_backup_email_now(is_auto=False)
                if ok:
                    messages.success(request, f"Settings saved & {msg}")
                else:
                    messages.warning(request, f"Settings saved, but email send reported: {msg}")
            else:
                messages.success(request, "Cloud Email Backup accounts (3 Options) & Auto-Timer settings saved successfully.")
            return redirect("school_settings")

        form = SchoolSettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "School profile & configuration updated successfully.")
            return redirect("school_settings")
    else:
        form = SchoolSettingForm(instance=setting)

    backup_logs = BackupHistoryLog.objects.all()[:10]
    return render(
        request,
        "school/settings.html",
        {
            "form": form,
            "setting": setting,
            "email_accounts": email_accounts,
            "backup_logs": backup_logs,
        },
    )


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
    from teachers.models import Teacher

    classes = ClassLevel.objects.prefetch_related("sections__teacher").all()
    all_teachers = Teacher.objects.filter(status="Active").order_by("teacher_id")

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
        {
            "classes": classes,
            "form": form,
            "section_form": section_form,
            "all_teachers": all_teachers,
        },
    )


@login_required
def section_create(request):
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            sec = form.save()
            if sec.teacher and not sec.teacher.assigned_section:
                sec.teacher.assigned_section = f"{sec.class_level.name} - {sec.name}"
                sec.teacher.save(update_fields=["assigned_section"])
            messages.success(request, "Section created successfully.")
        else:
            messages.error(request, "Error creating section. Ensure section name is unique for the class.")
    return redirect("class_list")


@login_required
def section_update_teacher(request, pk):
    """
    Assign or update the Class Teacher for a specific Section directly from the Classes & Sections page.
    """
    from teachers.models import Teacher

    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id", "").strip()
        custom_name = request.POST.get("class_teacher", "").strip()
        if teacher_id:
            t_obj = Teacher.objects.filter(pk=teacher_id).first()
            section.teacher = t_obj
            section.class_teacher = custom_name or (t_obj.full_name if t_obj else "")
            if t_obj:
                t_obj.assigned_section = f"{section.class_level.name} - {section.name}"
                t_obj.save(update_fields=["assigned_section"])
        else:
            section.teacher = None
            section.class_teacher = custom_name
        section.save()
        messages.success(request, f"Updated Class Teacher for {section.class_level.name} - Section {section.name}.")
    return redirect("class_list")


@login_required
def export_classes_excel(request):
    """
    Export all Class Levels, Sections, and their Assigned Section Teachers (Name, Father Name, Contact) to Excel.
    """
    from students.models import Student
    classes = ClassLevel.objects.prefetch_related("sections__teacher").all()
    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Class Name",
        "Academic Level",
        "Standard Monthly Fee (PKR)",
        "Sections",
        "Section Teachers (Name / Father / Contact)",
        "Total Active Students",
    ]

    rows = []
    for c in classes:
        secs = list(c.sections.all())
        sec_names = ", ".join([s.name for s in secs]) or "None"
        teacher_details = []
        for s in secs:
            if s.teacher:
                t = s.teacher
                info = f"Sec {s.name}: {t.full_name}"
                if t.father_name:
                    info += f" (S/D/O {t.father_name})"
                if t.contact_number:
                    info += f" [{t.contact_number}]"
                teacher_details.append(info)
            elif s.class_teacher:
                teacher_details.append(f"Sec {s.name}: {s.class_teacher}")
        student_count = Student.objects.filter(current_class=c, status="Active").count()
        rows.append([
            c.name,
            c.level,
            float(c.monthly_fee),
            sec_names,
            " | ".join(teacher_details) if teacher_details else "Unassigned",
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
    Central Data Exchange & Full Backup Hub:
    Allows one-stop downloading of Full .SQL & 16-Sheet Master .XLSX backups,
    one-click Full Restore (.sql / .xlsx), Cloud Email Backup, and module exports/imports.
    """
    from exams.models import ExamMark
    from finance.models import FeePaymentReceipt
    from students.models import Student
    from teachers.models import Teacher

    active_students = Student.objects.filter(status="Active").count()
    total_students = Student.objects.count()
    active_teachers = Teacher.objects.filter(status="Active").count()
    total_classes = ClassLevel.objects.count()
    total_sections = Section.objects.count()
    total_exam_marks = ExamMark.objects.count()
    total_fee_receipts = FeePaymentReceipt.objects.count()

    context = {
        "active_students": active_students,
        "total_students": total_students,
        "active_teachers": active_teachers,
        "total_classes": total_classes,
        "total_sections": total_sections,
        "total_exam_marks": total_exam_marks,
        "total_fee_receipts": total_fee_receipts,
        "email_accounts": BackupEmailAccount.ensure_three_slots(),
        "backup_logs": BackupHistoryLog.objects.all()[:8],
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


def license_expired(request):
    """
    Subscription / License Expiration Notice:
    Displayed when a school trial or subscription period has elapsed.
    Presents client school status and developer contact channels (Phone & WhatsApp).
    """
    lic = SoftwareLicense.get_license()
    if lic.is_valid():
        return redirect("dashboard")
    return render(request, "license/expired.html", {"license": lic})


def license_developer_portal(request):
    """
    Secure Developer & Vendor License Management Console:
    Strictly protected by Developer Master Key / PIN.
    Only the real software developer holding the exact Master Key can access and modify software licensing.
    """
    import time
    from django.contrib.auth.hashers import check_password, make_password

    lic = SoftwareLicense.get_license()
    # Developer session MUST be specifically unlocked via Master PIN (no school superuser bypass)
    is_authenticated = request.session.get("dev_portal_auth", False)

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "verify_pin":
            # Brute-force protection: rate limit invalid attempts
            now_ts = int(time.time())
            failed_attempts = request.session.get("dev_pin_failed_attempts", 0)
            lockout_until = request.session.get("dev_pin_lockout_until", 0)

            if now_ts < lockout_until:
                remaining_wait = lockout_until - now_ts
                messages.error(request, f"Too many incorrect attempts. Please wait {remaining_wait} seconds.")
                return redirect("license_developer_portal")

            entered_pin = request.POST.get("developer_pin", "").strip()

            def verify_developer_pin(input_pin, stored_pin):
                if not input_pin or not stored_pin:
                    return False
                # Direct match
                if input_pin == stored_pin:
                    return True
                # Constant-time comparison
                import hmac
                if hmac.compare_digest(input_pin, stored_pin):
                    return True
                # If stored as Django password hash
                try:
                    if stored_pin.startswith(("pbkdf2_", "argon2", "bcrypt")):
                        return check_password(input_pin, stored_pin)
                except Exception:
                    pass
                return False

            if verify_developer_pin(entered_pin, lic.developer_master_pin):
                # Successful verification
                request.session["dev_portal_auth"] = True
                request.session["dev_pin_failed_attempts"] = 0
                request.session.pop("dev_pin_lockout_until", None)
                messages.success(request, "Developer Master Key verified successfully. Access granted.")
                return redirect("license_developer_portal")
            else:
                failed_attempts += 1
                request.session["dev_pin_failed_attempts"] = failed_attempts
                if failed_attempts >= 5:
                    request.session["dev_pin_lockout_until"] = now_ts + 60  # 60s cooldown
                    messages.error(request, "Incorrect Developer PIN! 5 failed attempts reached. Locked for 60 seconds.")
                else:
                    messages.error(request, f"Access Denied: Invalid Developer PIN ({5 - failed_attempts} attempts remaining).")
                return redirect("license_developer_portal")

        if not is_authenticated:
            messages.error(request, "Access Denied: Master Developer Authentication required.")
            return redirect("license_developer_portal")

        if action == "logout_dev":
            request.session.pop("dev_portal_auth", None)
            messages.info(request, "Developer session closed.")
            return redirect("license_developer_portal")

        if action == "extend_preset":
            preset = request.POST.get("preset", "")
            now = timezone.now()
            base_time = lic.expires_at if (lic.expires_at and lic.expires_at > now) else now

            if preset == "15m":
                lic.expires_at = base_time + timedelta(minutes=15)
            elif preset == "1h":
                lic.expires_at = base_time + timedelta(hours=1)
            elif preset == "2h":
                lic.expires_at = base_time + timedelta(hours=2)
            elif preset == "1d":
                lic.expires_at = base_time + timedelta(days=1)
            elif preset == "7d":
                lic.expires_at = base_time + timedelta(days=7)
            elif preset == "30d":
                lic.expires_at = base_time + timedelta(days=30)
            elif preset == "90d":
                lic.expires_at = base_time + timedelta(days=90)
            elif preset == "180d":
                lic.expires_at = base_time + timedelta(days=180)
            elif preset == "365d":
                lic.expires_at = base_time + timedelta(days=365)
            elif preset == "730d":
                lic.expires_at = base_time + timedelta(days=730)

            lic.is_active = True
            lic.save()
            messages.success(request, f"License successfully extended! New expiry: {lic.expires_at.strftime('%d-%b-%Y %I:%M %p')}.")
            return redirect("license_developer_portal")

        if action == "save_custom":
            custom_datetime_str = request.POST.get("custom_expires_at", "").strip()
            client_name = request.POST.get("client_name", "").strip()
            dev_phone = request.POST.get("developer_phone", "").strip()
            dev_whatsapp = request.POST.get("developer_whatsapp", "").strip()
            dev_email = request.POST.get("developer_email", "").strip()
            new_pin = request.POST.get("new_developer_pin", "").strip()
            notes = request.POST.get("notes", "").strip()

            if custom_datetime_str:
                for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        parsed_dt = datetime.strptime(custom_datetime_str, fmt)
                        lic.expires_at = timezone.make_aware(parsed_dt) if timezone.is_naive(parsed_dt) else parsed_dt
                        break
                    except ValueError:
                        pass

            if client_name:
                lic.client_name = client_name
            if dev_phone:
                lic.developer_phone = dev_phone
            if dev_whatsapp:
                lic.developer_whatsapp = dev_whatsapp
            if dev_email:
                lic.developer_email = dev_email
            if new_pin:
                lic.developer_master_pin = new_pin
            if notes is not None:
                lic.notes = notes

            lic.is_active = True
            lic.save()
            messages.success(request, f"License settings updated. Active until {lic.expires_at.strftime('%d-%b-%Y %I:%M %p')}.")
            return redirect("license_developer_portal")

        if action == "lock_now":
            lic.expires_at = timezone.now() - timedelta(minutes=1)
            lic.save()
            messages.warning(request, "Software license immediately locked for testing.")
            return redirect("license_expired")

    return render(
        request,
        "license/portal.html",
        {
            "license": lic,
            "is_authenticated": is_authenticated,
        },
    )


