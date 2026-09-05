from datetime import date, datetime
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from school.excel_utils import (
    create_styled_workbook,
    excel_download_response,
    parse_excel_upload,
)
from school.models import SchoolSetting

from .forms import (
    GenerateSalaryBillsForm,
    MonthlySalaryBillForm,
    SalaryScaleForm,
    TeacherForm,
)
from .models import MonthlySalaryBill, SalaryScale, Teacher
from school.whatsapp_utils import build_teacher_salary_slip_msg


@login_required
def teacher_list(request):
    """
    Teacher / Staff list (FR-6.3).
    """
    teachers = Teacher.objects.select_related("salary_scale").all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query)
            | Q(teacher_id__icontains=query)
            | Q(designation__icontains=query)
            | Q(contact_number__icontains=query)
        )
    if status:
        teachers = teachers.filter(status=status)

    return render(
        request,
        "teachers/teacher_list.html",
        {"teachers": teachers, "query": query, "selected_status": status},
    )


@login_required
def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher {teacher.full_name} added successfully.")
            return redirect("teacher_detail", pk=teacher.pk)
    else:
        form = TeacherForm()
    return render(request, "teachers/teacher_form.html", {"form": form, "title": "Add New Teacher / Staff"})


@login_required
def teacher_detail(request, pk):
    """
    Staff detail page showing profile plus full salary-bill history (most recent first) (FR-6.3).
    """
    teacher = get_object_or_404(
        Teacher.objects.select_related("salary_scale"), pk=pk
    )
    salary_bills = teacher.salary_bills.order_by("-year", "-month")
    return render(
        request,
        "teachers/teacher_detail.html",
        {"teacher": teacher, "salary_bills": salary_bills},
    )


@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Teacher {teacher.full_name} updated successfully.")
            return redirect("teacher_detail", pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(
        request,
        "teachers/teacher_form.html",
        {"form": form, "teacher": teacher, "title": f"Edit Teacher: {teacher.full_name}"},
    )


@login_required
def experience_certificate(request, pk):
    """
    Printable Staff Experience Certificate (FR-6.8, FR-8.3).
    """
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "teachers/experience_certificate.html", {"teacher": teacher})


@login_required
def staff_id_card(request, pk):
    """
    Printable Staff ID Card (FR-6.8, FR-8.3).
    """
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "teachers/staff_id_card.html", {"teacher": teacher})


@login_required
def salary_bill_list(request):
    """
    Salary bill list filterable by month and year (FR-6.7).
    """
    today = timezone.now().date()
    month = request.GET.get("month", str(today.month))
    year = request.GET.get("year", str(today.year))

    bills = MonthlySalaryBill.objects.select_related("teacher").all()
    if month:
        bills = bills.filter(month=int(month))
    if year:
        bills = bills.filter(year=int(year))

    total_net = sum(b.net_payable for b in bills)
    total_paid = sum(b.actual_paid for b in bills)
    total_balance_left = sum(b.balance_left for b in bills)

    for b in bills:
        b.whatsapp_url = build_teacher_salary_slip_msg(b)["url"]

    import calendar
    context = {
        "bills": bills,
        "selected_month": int(month) if month else "",
        "selected_year": int(year) if year else "",
        "selected_month_name": calendar.month_name[int(month)] if month else "All Months",
        "total_net": total_net,
        "total_paid": total_paid,
        "total_balance_left": total_balance_left,
        "months": [(i, calendar.month_name[i]) for i in range(1, 13)],
    }
    return render(request, "teachers/salary_bill_list.html", context)


@login_required
def export_salary_bills_excel(request):
    """
    Export monthly salary bills to Excel spreadsheet with gross, deductions,
    absent cuts, net payable, actual paid, and remaining balance left to teacher.
    """
    import calendar
    from school.excel_utils import create_styled_workbook, excel_download_response

    today = timezone.now().date()
    month = request.GET.get("month", str(today.month))
    year = request.GET.get("year", str(today.year))

    bills = MonthlySalaryBill.objects.select_related("teacher", "teacher__salary_scale").all()
    if month:
        bills = bills.filter(month=int(month))
    if year:
        bills = bills.filter(year=int(year))

    headers = [
        "Bill #",
        "Staff ID",
        "Teacher Full Name",
        "Designation",
        "Month",
        "Year",
        "Days Present",
        "Days Absent",
        "Basic Pay (PKR)",
        "Allowances (PKR)",
        "Gross Earnings (PKR)",
        "Absent Cut (PKR)",
        "Other Deductions (PKR)",
        "Total Deductions (PKR)",
        "Net Payable (PKR)",
        "Amount Paid (PKR)",
        "Balance Left (PKR)",
        "Payment Status",
        "Payment Date",
    ]

    rows = []
    for b in bills:
        m_name = calendar.month_name[b.month] if 1 <= b.month <= 12 else str(b.month)
        status_label = "Cleared" if b.payment_status == "Cleared" else ("Partial" if b.payment_status == "Partial" else "Pending")
        rows.append([
            b.id,
            b.teacher.teacher_id,
            b.teacher.full_name,
            b.teacher.designation,
            m_name,
            b.year,
            b.days_present,
            b.absent_days,
            float(b.base_pay),
            float(b.allowances),
            float(b.gross_pay),
            float(b.auto_absent_deduction),
            float(b.other_deductions),
            float(b.deductions),
            float(b.net_payable),
            float(b.actual_paid),
            float(b.balance_left),
            status_label,
            b.payment_date.strftime("%Y-%m-%d") if b.payment_date else "",
        ])

    m_str = calendar.month_name[int(month)] if month else "All"
    y_str = year or today.year
    buffer = create_styled_workbook(f"Salary Bills {m_str} {y_str}", headers, rows)
    return excel_download_response(buffer, f"KMS_Salary_Bills_{m_str}_{y_str}.xlsx")


@login_required
def salary_bill_detail(request, pk):
    """
    Printable Salary Slip Detail View (FR-6.7).
    """
    bill = get_object_or_404(
        MonthlySalaryBill.objects.select_related("teacher", "teacher__salary_scale"),
        pk=pk,
    )
    whatsapp_data = build_teacher_salary_slip_msg(
        bill,
        principal_name="Farman Ali",
        principal_contact="0344-9631323",
        vp_name="Umar Saeed",
        vp_contact="0345-3407095",
    )
    context = {
        "bill": bill,
        "today": timezone.now().date(),
        "principal_name": "Farman Ali",
        "principal_contact": "0344-9631323",
        "vp_name": "Umar Saeed",
        "vp_contact": "0345-3407095",
        "developer_name": "Rashid Zada",
        "developer_contact": "0347-0983567",
        "admin_name": "Rashid Zada",
        "admin_contact": "0347-0983567",
        "whatsapp_data": whatsapp_data,
    }
    return render(request, "teachers/salary_bill_detail.html", context)


@login_required
def salary_bill_update(request, pk):
    """
    Edit individual salary bill (FR-6.6).
    """
    bill = get_object_or_404(MonthlySalaryBill, pk=pk)
    if request.method == "POST":
        form = MonthlySalaryBillForm(request.POST, instance=bill)
        if form.is_valid():
            updated_bill = form.save(commit=False)
            if updated_bill.is_paid and not updated_bill.payment_date:
                updated_bill.payment_date = timezone.now().date()
            updated_bill.save()
            messages.success(request, f"Salary bill for {bill.teacher.full_name} updated.")
            return redirect("salary_bill_list")
    else:
        form = MonthlySalaryBillForm(instance=bill)

    return render(
        request,
        "teachers/salary_bill_form.html",
        {"form": form, "bill": bill},
    )


@login_required
def generate_salary_bills(request):
    """
    Batch generate salary bills for active teachers with assigned salary scales (FR-6.4, Rule 9).
    """
    today = timezone.now().date()
    if request.method == "POST":
        form = GenerateSalaryBillsForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])

            active_teachers = Teacher.objects.filter(
                status="Active", salary_scale__isnull=False
            ).select_related("salary_scale")

            created_count = 0
            with transaction.atomic():
                for teacher in active_teachers:
                    if not MonthlySalaryBill.objects.filter(
                        teacher=teacher, month=month, year=year
                    ).exists():
                        scale = teacher.salary_scale
                        MonthlySalaryBill.objects.create(
                            teacher=teacher,
                            month=month,
                            year=year,
                            base_pay=scale.basic_pay,
                            days_present=30,
                            allowances=scale.total_allowances,
                            deductions=Decimal("0.00"),
                            is_paid=False,
                        )
                        created_count += 1

            messages.success(
                request,
                f"Generated {created_count} salary bills for {month}/{year}.",
            )
            return redirect(f"/teachers/salary-bills/?month={month}&year={year}")
    else:
        form = GenerateSalaryBillsForm(initial={"month": today.month, "year": today.year})

    return render(
        request, "teachers/generate_salary_bills.html", {"form": form}
    )


@login_required
def salary_scale_list(request):
    scales = SalaryScale.objects.all()
    if request.method == "POST":
        form = SalaryScaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salary scale added successfully.")
            return redirect("salary_scale_list")
    else:
        form = SalaryScaleForm()
    return render(
        request, "teachers/salary_scale_list.html", {"scales": scales, "form": form}
    )


@login_required
def export_teachers_excel(request):
    """
    Exports all or filtered teachers to a professionally styled Excel sheet.
    """
    teachers = Teacher.objects.select_related("salary_scale").all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query)
            | Q(teacher_id__icontains=query)
            | Q(designation__icontains=query)
            | Q(contact_number__icontains=query)
        )
    if status:
        teachers = teachers.filter(status=status)

    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Staff ID",
        "Full Name",
        "Father / Husband Name",
        "Designation",
        "CNIC",
        "Date of Birth",
        "Contact Number",
        "Address",
        "Qualification",
        "Experience",
        "Joining Date",
        "Salary Scale",
        "Basic Pay (PKR)",
        "Gross Salary (PKR)",
        "Status",
    ]

    rows = []
    for t in teachers:
        scale_name = t.salary_scale.name if t.salary_scale else "-"
        basic_pay = float(t.salary_scale.basic_pay) if t.salary_scale else 0.0
        gross_salary = float(t.salary_scale.gross_salary) if t.salary_scale else 0.0

        rows.append([
            t.teacher_id,
            t.full_name,
            t.father_name or "-",
            t.designation or "Teacher",
            t.cnic or "-",
            str(t.dob) if t.dob else "-",
            t.contact_number or "-",
            t.address or "-",
            t.qualification or "-",
            t.experience or "-",
            str(t.joining_date) if t.joining_date else "-",
            scale_name,
            basic_pay,
            gross_salary,
            t.status,
        ])

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"Teachers_Staff_Export_{timestamp}.xlsx"
    buffer = create_styled_workbook("Teachers & Staff Directory", headers, rows, school_name=school_name)
    return excel_download_response(buffer, filename)


@login_required
def download_teacher_template(request):
    """
    Downloads a pre-formatted Excel template with sample teacher records.
    """
    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Staff ID *",
        "Full Name *",
        "Father / Husband Name",
        "Designation *",
        "CNIC",
        "Date of Birth (YYYY-MM-DD) *",
        "Contact Number *",
        "Address",
        "Qualification",
        "Experience",
        "Joining Date (YYYY-MM-DD)",
        "Salary Scale Name",
        "Status (Active/Inactive)",
    ]

    sample_rows = [
        [
            "TCH-001",
            "Muhammad Tariq",
            "Abdul Rashid",
            "Senior Science Teacher",
            "15602-1234567-1",
            "1990-05-15",
            "0345-9876543",
            "Barikot, Swat",
            "M.Sc Physics, B.Ed",
            "5 Years teaching experience in High School",
            "2021-08-01",
            "BPS-16",
            "Active",
        ],
        [
            "TCH-002",
            "Fatima Bibi",
            "Muhammad Ishaq",
            "Junior English Teacher",
            "15602-7654321-2",
            "1995-10-20",
            "0300-5554321",
            "Qalagay, Swat",
            "M.A English",
            "3 Years at Primary Level",
            "2023-03-01",
            "BPS-14",
            "Active",
        ],
    ]

    buffer = create_styled_workbook("Teachers Onboarding Template", headers, sample_rows, school_name=school_name)
    return excel_download_response(buffer, "KMS_Teacher_Import_Template.xlsx")


@login_required
def import_teachers_excel(request):
    """
    Imports teachers/staff from an uploaded Excel file.
    Auto-links or creates salary scales, handles duplicate staff IDs gracefully.
    """
    if request.method != "POST" or "excel_file" not in request.FILES:
        messages.error(request, "Please choose a valid Excel (.xlsx) file to upload.")
        return redirect("teacher_list")

    excel_file = request.FILES["excel_file"]
    records, errors = parse_excel_upload(excel_file, header_row=2)

    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect("teacher_list")

    if not records:
        messages.warning(request, "The uploaded Excel file contains no staff data rows.")
        return redirect("teacher_list")

    success_count = 0
    row_errors = []

    def parse_date(val):
        if not val:
            return None
        if isinstance(val, (datetime, date)):
            return val if isinstance(val, date) else val.date()
        val_str = str(val).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val_str, fmt).date()
            except ValueError:
                continue
        return None

    existing_ids = set(Teacher.objects.values_list("teacher_id", flat=True))
    id_counter = 1

    with transaction.atomic():
        for r in records:
            row_num = r.get("_row_number", "?")
            full_name = str(r.get("full_name__", "") or r.get("full_name", "")).strip()

            if not full_name:
                row_errors.append(f"Row {row_num}: Missing Full Name.")
                continue

            staff_id = str(r.get("staff_id__", "") or r.get("staff_id", "") or r.get("teacher_id", "")).strip()
            if not staff_id or staff_id in existing_ids:
                while f"TCH-{id_counter:03d}" in existing_ids:
                    id_counter += 1
                staff_id = f"TCH-{id_counter:03d}"
                id_counter += 1
            existing_ids.add(staff_id)

            father_name = str(r.get("father___husband_name", "") or r.get("father_name", "")).strip()
            designation = str(r.get("designation__", "") or r.get("designation", "Teacher")).strip() or "Teacher"
            cnic = str(r.get("cnic", "") or "").strip()
            contact = str(r.get("contact_number__", "") or r.get("contact_number", "")).strip()
            address = str(r.get("address", "") or "").strip()
            qualification = str(r.get("qualification", "") or "").strip()
            experience = str(r.get("experience", "") or "").strip()

            dob = parse_date(r.get("date_of_birth__yyyy_mm_dd____", None) or r.get("date_of_birth", None)) or date(1990, 1, 1)
            joining_date = parse_date(r.get("joining_date__yyyy_mm_dd_", None) or r.get("joining_date", None)) or timezone.now().date()

            status_raw = str(r.get("status__active_inactive_", "") or r.get("status", "Active")).strip().capitalize()
            status = "Inactive" if "inactive" in status_raw.lower() else "Active"

            scale_name = str(r.get("salary_scale_name", "") or r.get("salary_scale", "")).strip()
            salary_scale = None
            if scale_name and scale_name != "-":
                salary_scale = SalaryScale.objects.filter(name__iexact=scale_name).first()
                if not salary_scale:
                    salary_scale = SalaryScale.objects.create(
                        name=scale_name,
                        basic_pay=Decimal("25000.00"),
                        medical_allowance=Decimal("2000.00"),
                        conveyance_allowance=Decimal("3000.00"),
                    )

            Teacher.objects.create(
                teacher_id=staff_id,
                full_name=full_name,
                father_name=father_name,
                designation=designation,
                cnic=cnic,
                dob=dob,
                contact_number=contact,
                address=address,
                qualification=qualification,
                experience=experience,
                joining_date=joining_date,
                salary_scale=salary_scale,
                status=status,
            )
            success_count += 1

    if success_count > 0:
        messages.success(request, f"Excel Import Completed! Successfully imported {success_count} staff / teacher records.")
    if row_errors:
        messages.warning(request, f"Some rows were skipped: {'; '.join(row_errors[:5])}")

    return redirect("teacher_list")

