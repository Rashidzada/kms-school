import calendar
import io
import json
from datetime import date, datetime, time
from decimal import Decimal
import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from school.excel_utils import (
    create_styled_workbook,
    excel_download_response,
    parse_excel_upload,
)
from school.models import SchoolSetting

from .forms import (
    BiometricImportForm,
    GenerateSalaryBillsForm,
    MonthlySalaryBillForm,
    SalaryScaleForm,
    TeacherAttendanceSettingForm,
    TeacherForm,
    TeacherLoanForm,
    TeacherLoanRepaymentForm,
)
from .models import (
    MonthlySalaryBill,
    SalaryScale,
    Teacher,
    TeacherAttendance,
    TeacherAttendanceSetting,
    TeacherLoan,
    TeacherLoanRepayment,
)
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
    school_setting = SchoolSetting.objects.first()
    all_teachers = Teacher.objects.filter(status="Active").order_by("teacher_id")
    return render(
        request,
        "teachers/staff_id_card.html",
        {
            "teacher": teacher,
            "school_setting": school_setting,
            "all_teachers": all_teachers,
        },
    )


@login_required
def all_staff_id_cards(request):
    """
    Printable batch sheet of full professional Faculty ID Cards for all active teachers (A4 batch sheet).
    """
    teachers = Teacher.objects.filter(status="Active").order_by("teacher_id")
    school_setting = SchoolSetting.objects.first()
    return render(
        request,
        "teachers/staff_id_cards_batch_print.html",
        {"teachers": teachers, "school_setting": school_setting},
    )


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


def calculate_length_of_service(start_date, end_date=None):
    """
    Computes exact length of service formatted as:
    '05 Years 11 Months 19 Days'
    """
    if not start_date:
        return "---"
    if not end_date:
        end_date = timezone.now().date()
    if start_date > end_date:
        return "00 Years 00 Months 00 Days"

    import calendar
    years = end_date.year - start_date.year
    months = end_date.month - start_date.month
    days = end_date.day - start_date.day
    if days < 0:
        months -= 1
        prev_month = 12 if end_date.month == 1 else end_date.month - 1
        prev_year = end_date.year - 1 if end_date.month == 1 else end_date.year
        _, prev_days = calendar.monthrange(prev_year, prev_month)
        days += prev_days
    if months < 0:
        years -= 1
        months += 12
    return f"{years:02d} Years {months:02d} Months {days:02d} Days"


@login_required
def salary_bill_detail(request, pk):
    """
    Official Monthly Salary Statement View matching Accounts Office format for private school.
    """
    bill = get_object_or_404(
        MonthlySalaryBill.objects.select_related("teacher", "teacher__salary_scale"),
        pk=pk,
    )
    whatsapp_data = build_teacher_salary_slip_msg(
        bill,
        principal_name="Dr. Farman Ali",
        principal_contact="+92 344 9631323",
        vp_name="Umar Saeed",
        vp_contact="+92 345 3407095",
    )

    # 1. Calculate Length of Service
    today_date = timezone.now().date()
    length_of_service = calculate_length_of_service(bill.teacher.joining_date, bill.payment_date or today_date)

    # 2. Structured Pay & Allowances (4-column wage matrix)
    allowance_items = []
    allowance_items.append({"code": "0001", "name": "Basic Pay", "amount": bill.base_pay})

    scale = getattr(bill.teacher, "salary_scale", None)
    if scale and scale.medical_allowance > 0:
        allowance_items.append({"code": "1001", "name": "Medical Allowance", "amount": scale.medical_allowance})
    if scale and scale.conveyance_allowance > 0:
        allowance_items.append({"code": "1210", "name": "Conveyance Allowance", "amount": scale.conveyance_allowance})
    if scale and scale.other_allowances > 0:
        allowance_items.append({"code": "1911", "name": "Teaching / Special Allowance", "amount": scale.other_allowances})

    # Account for any remaining or custom allowances
    scale_total_allw = scale.total_allowances if scale else Decimal("0.00")
    if bill.allowances > scale_total_allw:
        diff = bill.allowances - scale_total_allw
        allowance_items.append({"code": "2378", "name": "Performance / Adhoc Relief", "amount": diff})
    elif not scale and bill.allowances > 0:
        half1 = (bill.allowances * Decimal("0.5")).quantize(Decimal("0.01"))
        half2 = bill.allowances - half1
        allowance_items.append({"code": "1210", "name": "Conveyance Allowance", "amount": half1})
        allowance_items.append({"code": "2316", "name": "Teaching Allowance", "amount": half2})

    # Pad to even count for 2-column paired layout
    if len(allowance_items) % 2 != 0:
        allowance_items.append({"code": "----", "name": "---", "amount": None})

    allowance_pairs = []
    for i in range(0, len(allowance_items), 2):
        allowance_pairs.append({
            "left": allowance_items[i],
            "right": allowance_items[i + 1] if (i + 1) < len(allowance_items) else None,
        })

    # 3. Structured Deductions (Private School - No GPF)
    deduction_items = []
    if bill.auto_absent_deduction > 0:
        deduction_items.append({
            "code": "3001",
            "name": f"Absence Deduction ({bill.absent_days} days)",
            "amount": -bill.auto_absent_deduction,
        })
    if bill.other_deductions > 0:
        deduction_items.append({
            "code": "3990",
            "name": "Advance Salary / Loan Recovery",
            "amount": -bill.other_deductions,
        })

    # If no deductions, show standard zero entries
    if not deduction_items:
        deduction_items.append({
            "code": "3001",
            "name": "Absence Deduction (0 days)",
            "amount": Decimal("0.00"),
        })
        deduction_items.append({
            "code": "3990",
            "name": "Advance Salary / Loan Recovery",
            "amount": Decimal("0.00"),
        })

    if len(deduction_items) % 2 != 0:
        deduction_items.append({"code": "----", "name": "Staff Welfare / Security Fund", "amount": Decimal("0.00")})

    deduction_pairs = []
    for i in range(0, len(deduction_items), 2):
        deduction_pairs.append({
            "left": deduction_items[i],
            "right": deduction_items[i + 1] if (i + 1) < len(deduction_items) else None,
        })

    # 4. Previous Unpaid Months Breakdown (e.g. Jan + Feb unpaid)
    unpaid_previous_bills = bill.get_unpaid_previous_bills()
    active_loans = bill.get_active_loans()
    total_loan_outstanding = bill.total_outstanding_loan
    effective_loan_deduction = bill.effective_loan_deduction

    context = {
        "bill": bill,
        "today": today_date,
        "length_of_service": length_of_service,
        "allowance_pairs": allowance_pairs,
        "deduction_pairs": deduction_pairs,
        "unpaid_previous_bills": unpaid_previous_bills,
        "calculated_previous_dues": bill.calculated_previous_dues,
        "effective_previous_dues": bill.effective_previous_dues,
        "active_loans": active_loans,
        "total_loan_outstanding": total_loan_outstanding,
        "effective_loan_deduction": effective_loan_deduction,
        "total_gross_payable": bill.total_gross_payable,
        "final_net_payable": bill.final_net_payable,
        "final_balance_left": max(Decimal("0.00"), bill.final_net_payable - bill.actual_paid),
        "principal_name": "Dr. Farman Ali",
        "principal_contact": "+92 344 9631323",
        "vp_name": "Umar Saeed",
        "vp_contact": "+92 345 3407095",
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
    Edit individual salary bill with custom old dues and loan installment deduction options.
    """
    bill = get_object_or_404(MonthlySalaryBill, pk=pk)
    active_loans = bill.get_active_loans()
    unpaid_bills = bill.get_unpaid_previous_bills()
    suggested_dues = bill.calculated_previous_dues
    suggested_loan_cut = active_loans.first().monthly_installment if active_loans.exists() else Decimal("0.00")

    if request.method == "POST":
        form = MonthlySalaryBillForm(request.POST, instance=bill)
        if form.is_valid():
            with transaction.atomic():
                updated_bill = form.save(commit=False)
                if updated_bill.is_paid and not updated_bill.payment_date:
                    updated_bill.payment_date = timezone.now().date()
                updated_bill.save()

                # Process Loan Repayment if custom deduct_loan is toggled ON
                if updated_bill.deduct_loan and updated_bill.loan_deduction_amount > 0 and active_loans.exists():
                    target_loan = active_loans.first()
                    repay_obj, _ = TeacherLoanRepayment.objects.get_or_create(
                        loan=target_loan,
                        salary_bill=updated_bill,
                        defaults={
                            "amount": updated_bill.loan_deduction_amount,
                            "payment_date": updated_bill.payment_date or timezone.now().date(),
                            "payment_method": "Salary Deduction",
                            "notes": f"Salary deduction for {updated_bill.month_name} {updated_bill.year}",
                        }
                    )
                    repay_obj.amount = updated_bill.loan_deduction_amount
                    repay_obj.save()

                    # Recalculate total_repaid on loan
                    total_rep = sum(r.amount for r in target_loan.repayments.all())
                    target_loan.total_repaid = total_rep
                    target_loan.save()
                elif not updated_bill.deduct_loan or updated_bill.loan_deduction_amount <= 0:
                    # Remove any existing salary deduction repayment for this bill if untoggled
                    reps = TeacherLoanRepayment.objects.filter(salary_bill=updated_bill)
                    for r in reps:
                        l = r.loan
                        r.delete()
                        l.total_repaid = sum(x.amount for x in l.repayments.all())
                        l.save()

            messages.success(request, f"Salary bill for {bill.teacher.full_name} updated successfully.")
            return redirect("salary_bill_detail", pk=bill.pk)
    else:
        # Pre-populate suggested dues or loan cut if not previously set
        initial_data = {}
        if not bill.previous_unpaid_dues and suggested_dues > 0:
            initial_data["previous_unpaid_dues"] = suggested_dues
        if not bill.loan_deduction_amount and suggested_loan_cut > 0:
            initial_data["loan_deduction_amount"] = suggested_loan_cut
        form = MonthlySalaryBillForm(instance=bill, initial=initial_data if initial_data else None)

    return render(
        request,
        "teachers/salary_bill_form.html",
        {
            "form": form,
            "bill": bill,
            "active_loans": active_loans,
            "unpaid_bills": unpaid_bills,
            "suggested_dues": suggested_dues,
            "suggested_loan_cut": suggested_loan_cut,
        },
    )


# ==============================================================================
# TEACHER ADVANCE & LOAN MANAGEMENT (KMS FINANCIAL COMPONENT)
# ==============================================================================

@login_required
def teacher_loan_list(request):
    """
    Staff loans & advances overview with active balances, repayments, and teacher filtering.
    """
    loans_qs = TeacherLoan.objects.select_related("teacher").all()
    teacher_id = request.GET.get("teacher_id", "")
    status = request.GET.get("status", "")

    if teacher_id:
        loans_qs = loans_qs.filter(teacher_id=teacher_id)
    if status:
        loans_qs = loans_qs.filter(status=status)

    loans = list(loans_qs)
    total_principal = sum(l.principal_amount for l in loans)
    total_repaid = sum(l.total_repaid for l in loans)
    total_outstanding = sum(l.remaining_balance for l in loans)
    active_count = len([l for l in loans if not l.is_cleared])

    teachers = Teacher.objects.filter(status="Active").order_by("full_name")

    context = {
        "loans": loans,
        "teachers": teachers,
        "selected_teacher": teacher_id,
        "selected_status": status,
        "total_principal": total_principal,
        "total_repaid": total_repaid,
        "total_outstanding": total_outstanding,
        "active_count": active_count,
    }
    return render(request, "teachers/teacher_loan_list.html", context)


@login_required
def teacher_loan_create(request):
    """
    Issue a new loan / advance to a teacher or staff member.
    """
    if request.method == "POST":
        form = TeacherLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            messages.success(
                request,
                f"Loan of PKR {loan.principal_amount:,.2f} recorded for {loan.teacher.full_name}."
            )
            return redirect("teacher_loan_list")
    else:
        teacher_id = request.GET.get("teacher_id")
        initial = {"loan_date": timezone.now().date()}
        if teacher_id:
            initial["teacher"] = teacher_id
        form = TeacherLoanForm(initial=initial)

    return render(
        request,
        "teachers/teacher_loan_form.html",
        {"form": form, "title": "Record New Staff Loan / Advance"},
    )


@login_required
def teacher_loan_detail(request, pk):
    """
    View loan details, repayment history, and record manual cash/bank payment.
    """
    loan = get_object_or_404(TeacherLoan.objects.select_related("teacher"), pk=pk)
    repayments = loan.repayments.order_by("-payment_date", "-id")

    if request.method == "POST":
        repay_form = TeacherLoanRepaymentForm(request.POST)
        if repay_form.is_valid():
            with transaction.atomic():
                rep = repay_form.save(commit=False)
                rep.loan = loan
                rep.save()
                loan.total_repaid = sum(r.amount for r in loan.repayments.all())
                loan.save()
            messages.success(request, f"Payment of PKR {rep.amount:,.2f} recorded successfully.")
            return redirect("teacher_loan_detail", pk=loan.pk)
    else:
        repay_form = TeacherLoanRepaymentForm(initial={
            "payment_date": timezone.now().date(),
            "amount": min(loan.monthly_installment or loan.remaining_balance, loan.remaining_balance),
            "payment_method": "Cash",
        })

    return render(
        request,
        "teachers/teacher_loan_detail.html",
        {
            "loan": loan,
            "repayments": repayments,
            "repay_form": repay_form,
        },
    )


@login_required
def teacher_loan_delete(request, pk):
    """
    Delete a loan record.
    """
    loan = get_object_or_404(TeacherLoan, pk=pk)
    teacher_name = loan.teacher.full_name
    if request.method == "POST":
        loan.delete()
        messages.success(request, f"Loan record for {teacher_name} deleted.")
        return redirect("teacher_loan_list")
    return render(request, "teachers/teacher_loan_confirm_delete.html", {"loan": loan})


@login_required
def generate_salary_bills(request):
    """
    Batch generate salary bills for active teachers with assigned salary scales (FR-6.4, Rule 9),
    with intelligent attendance sync for late comers, absences, and bonuses.
    """
    today = timezone.now().date()
    if request.method == "POST":
        form = GenerateSalaryBillsForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])
            sync_attendance = form.cleaned_data.get("sync_attendance", True)

            active_teachers = Teacher.objects.filter(
                status="Active", salary_scale__isnull=False
            ).select_related("salary_scale")

            created_count = 0
            synced_count = 0
            with transaction.atomic():
                for teacher in active_teachers:
                    scale = teacher.salary_scale
                    bill, created = MonthlySalaryBill.objects.get_or_create(
                        teacher=teacher,
                        month=month,
                        year=year,
                        defaults={
                            "base_pay": scale.basic_pay,
                            "days_present": 30,
                            "allowances": scale.total_allowances,
                            "deductions": Decimal("0.00"),
                            "is_paid": False,
                        },
                    )
                    if created:
                        created_count += 1

                    if sync_attendance:
                        if bill.sync_from_attendance():
                            synced_count += 1

            msg = f"Generated {created_count} salary bills for {month}/{year}."
            if sync_attendance and synced_count > 0:
                msg += f" Successfully synced attendance cuts & bonuses for {synced_count} teachers."
            messages.success(request, msg)
            return redirect(f"/teachers/salary-bills/?month={month}&year={year}")
    else:
        form = GenerateSalaryBillsForm(initial={"month": today.month, "year": today.year, "sync_attendance": True})

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

    try:
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
    except Exception as e:
        messages.error(request, f"Excel Import Failed: {str(e)}")

    return redirect("teacher_list")


# ==============================================================================
# KMS V4 TEACHER ATTENDANCE, QR CODE & SALARY CUTTING SYSTEM
# ==============================================================================

@login_required
def teacher_qr_image(request, pk):
    """
    Dynamically stream crisp high-contrast PNG QR Code for staff attendance scanning.
    """
    teacher = get_object_or_404(Teacher, pk=pk)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(str(teacher.teacher_id))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response



@login_required
def qr_attendance_scan(request):
    """
    Live real-time QR Code scanning terminal for teacher check-in and check-out.
    """
    today = timezone.localtime(timezone.now()).date()
    setting = TeacherAttendanceSetting.get_settings()

    today_attendances = (
        TeacherAttendance.objects.filter(date=today)
        .select_related("teacher", "teacher__salary_scale")
        .order_by("-updated_at")
    )

    active_teachers = (
        Teacher.objects.filter(status="Active")
        .select_related("salary_scale")
        .order_by("full_name")
    )

    today_att_map = {a.teacher_id: a for a in today_attendances}
    for t in active_teachers:
        t.today_attendance = today_att_map.get(t.pk)

    total_active = active_teachers.count()
    present_count = today_attendances.filter(status="Present").count()
    late_count = today_attendances.filter(status="Late").count()
    absent_count = today_attendances.filter(status="Absent").count()
    half_day_count = today_attendances.filter(status="Half Day").count()
    total_deductions_today = sum(a.deduction_amount for a in today_attendances)

    context = {
        "today": today,
        "setting": setting,
        "today_attendances": today_attendances,
        "active_teachers": active_teachers,
        "total_active": total_active,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
        "half_day_count": half_day_count,
        "total_deductions_today": total_deductions_today,
    }
    return render(request, "teachers/qr_attendance_scan.html", context)


@login_required
def api_process_qr_scan(request):
    """
    AJAX handler for live QR barcode scans. Handles Check-in, Check-out,
    late minutes calculation, and instant hourly/daily cutting amounts.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST method required."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else request.POST
    except Exception:
        data = request.POST

    raw_code = str(data.get("code", "")).strip()
    if not raw_code:
        return JsonResponse({"success": False, "message": "No QR code detected."})

    clean_code = raw_code
    if "KMS-STAFF:" in raw_code.upper():
        clean_code = raw_code.split(":", 1)[1].strip()
    elif " - " in clean_code:
        clean_code = clean_code.split(" - ")[0].strip()

    teacher = Teacher.objects.filter(
        Q(teacher_id__iexact=clean_code) |
        Q(teacher_id__iexact=raw_code) |
        Q(full_name__iexact=clean_code)
    ).select_related("salary_scale").first()

    if not teacher and clean_code.isdigit():
        teacher = Teacher.objects.filter(pk=int(clean_code)).select_related("salary_scale").first()

    if not teacher:
        return JsonResponse({
            "success": False,
            "message": f"Staff ID '{raw_code}' not found in school database.",
        })


    now_dt = timezone.localtime(timezone.now())
    today = now_dt.date()
    now_time = now_dt.time().replace(microsecond=0)
    setting = TeacherAttendanceSetting.get_settings()

    att = TeacherAttendance.objects.filter(teacher=teacher, date=today).first()

    if not att:
        # First scan of the day -> Check In
        att = TeacherAttendance(
            teacher=teacher,
            date=today,
            check_in=now_time,
            attendance_method="QR Code",
            status="Present",
        )
        att.calculate_and_apply_deduction(setting)
        att.save()
        action = "check_in"
        msg = f"Check-In recorded at {now_time.strftime('%I:%M %p')}."
    else:
        # Subsequent scan -> Check Out
        if not att.check_out:
            att.check_out = now_time
            action = "check_out"
            msg = f"Check-Out recorded at {now_time.strftime('%I:%M %p')}."
        else:
            att.check_out = now_time
            action = "check_out_updated"
            msg = f"Check-Out updated to {now_time.strftime('%I:%M %p')}."

        att.calculate_and_apply_deduction(setting)
        att.save()

    photo_url = teacher.profile_picture.url if teacher.profile_picture else ""

    return JsonResponse({
        "success": True,
        "action": action,
        "message": msg,
        "teacher": {
            "id": teacher.pk,
            "staff_id": teacher.teacher_id,
            "name": teacher.full_name,
            "designation": teacher.designation,
            "photo_url": photo_url,
            "basic_pay": float(teacher.salary_scale.basic_pay) if (teacher.salary_scale and teacher.salary_scale.basic_pay) else 0.0,
        },
        "status": att.status,
        "check_in": att.check_in.strftime("%I:%M %p") if att.check_in else "",
        "check_out": att.check_out.strftime("%I:%M %p") if att.check_out else "",
        "late_minutes": att.late_minutes,
        "working_hours": float(att.working_hours),
        "deduction_amount": float(att.deduction_amount),
        "bonus_amount": float(att.bonus_amount),
    })


@login_required
def daily_attendance_register(request):
    """
    Daily manual attendance roster for all teachers. Allows rapid Present,
    Late, Absent, Half-day marking with custom salary cut and bonus overrides.
    """
    date_str = request.GET.get("date") or request.POST.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.localtime(timezone.now()).date()
    else:
        target_date = timezone.localtime(timezone.now()).date()

    setting = TeacherAttendanceSetting.get_settings()
    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")

    if request.method == "POST":
        action = request.POST.get("action", "save")
        with transaction.atomic():
            for t in teachers:
                prefix = f"teacher_{t.pk}_"
                status = request.POST.get(prefix + "status", "Present")
                check_in_str = request.POST.get(prefix + "check_in", "").strip()
                check_out_str = request.POST.get(prefix + "check_out", "").strip()
                deduction_str = request.POST.get(prefix + "deduction", "0.00").strip()
                bonus_str = request.POST.get(prefix + "bonus", "0.00").strip()
                remarks = request.POST.get(prefix + "remarks", "").strip()
                auto_calc = request.POST.get(prefix + "auto_calc", "off") == "on"

                check_in = None
                if check_in_str:
                    try:
                        check_in = datetime.strptime(check_in_str, "%H:%M").time()
                    except ValueError:
                        pass

                check_out = None
                if check_out_str:
                    try:
                        check_out = datetime.strptime(check_out_str, "%H:%M").time()
                    except ValueError:
                        pass

                try:
                    deduction_amount = Decimal(deduction_str or "0.00")
                except Exception:
                    deduction_amount = Decimal("0.00")

                try:
                    bonus_amount = Decimal(bonus_str or "0.00")
                except Exception:
                    bonus_amount = Decimal("0.00")

                att, _ = TeacherAttendance.objects.get_or_create(
                    teacher=t,
                    date=target_date,
                    defaults={"attendance_method": "Manual"}
                )
                att.status = status
                att.check_in = check_in
                att.check_out = check_out
                att.remarks = remarks
                att.bonus_amount = bonus_amount
                att.attendance_method = "Manual"

                if auto_calc or action == "auto_calculate_all":
                    att.calculate_and_apply_deduction(setting)
                else:
                    att.deduction_amount = deduction_amount
                    if att.check_in and setting.shift_start_time:
                        in_m = att.check_in.hour * 60 + att.check_in.minute
                        shift_m = setting.shift_start_time.hour * 60 + setting.shift_start_time.minute
                        att.late_minutes = max(0, in_m - shift_m)

                att.save()

        messages.success(request, f"Attendance register for {target_date.strftime('%d %b %Y')} saved successfully.")
        return redirect(f"{reverse('daily_attendance_register')}?date={target_date.strftime('%Y-%m-%d')}")

    existing_map = {
        a.teacher_id: a for a in TeacherAttendance.objects.filter(date=target_date)
    }

    attendance_rows = []
    for t in teachers:
        att = existing_map.get(t.pk)
        attendance_rows.append({
            "teacher": t,
            "attendance": att,
            "status": att.status if att else "Present",
            "check_in": att.check_in.strftime("%H:%M") if (att and att.check_in) else (setting.shift_start_time.strftime("%H:%M") if setting.shift_start_time else "08:00"),
            "check_out": att.check_out.strftime("%H:%M") if (att and att.check_out) else (setting.shift_end_time.strftime("%H:%M") if setting.shift_end_time else "12:30"),
            "deduction": att.deduction_amount if att else Decimal("0.00"),
            "bonus": att.bonus_amount if att else Decimal("0.00"),
            "late_minutes": att.late_minutes if att else 0,
            "remarks": att.remarks if att else "",
        })

    status_choices = [
        ("Present", "🟢 Present (Full Day)"),
        ("Late", "🟡 Late Comer"),
        ("Half Day", "🟠 Half Day"),
        ("Absent", "🔴 Absent"),
        ("Leave", "🔵 Leave (Approved)"),
        ("Holiday", "⚪ Holiday / Off Day"),
    ]

    school_setting = SchoolSetting.objects.first()

    context = {
        "target_date": target_date,
        "setting": setting,
        "school_setting": school_setting,
        "attendance_rows": attendance_rows,
        "status_choices": status_choices,
    }
    return render(request, "teachers/daily_attendance_register.html", context)


@login_required
def daily_attendance_print(request):
    """
    Printable / PDF report of Daily Faculty Attendance for Principal, Vice Principal & Admin.
    """
    date_str = request.GET.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.localtime(timezone.now()).date()
    else:
        target_date = timezone.localtime(timezone.now()).date()

    setting = TeacherAttendanceSetting.get_settings()
    school_setting = SchoolSetting.objects.first()
    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")

    existing_map = {
        a.teacher_id: a for a in TeacherAttendance.objects.filter(date=target_date)
    }

    attendance_rows = []
    present_cnt = 0
    late_cnt = 0
    absent_cnt = 0
    half_day_cnt = 0
    leave_cnt = 0
    holiday_cnt = 0
    total_deductions = Decimal("0.00")
    total_bonuses = Decimal("0.00")

    for t in teachers:
        att = existing_map.get(t.pk)
        status = att.status if att else "Present"

        if status == "Present":
            present_cnt += 1
        elif status == "Late":
            late_cnt += 1
        elif status == "Absent":
            absent_cnt += 1
        elif status == "Half Day":
            half_day_cnt += 1
        elif status == "Leave":
            leave_cnt += 1
        elif status == "Holiday":
            holiday_cnt += 1

        ded = att.deduction_amount if att else Decimal("0.00")
        bon = att.bonus_amount if att else Decimal("0.00")
        total_deductions += ded
        total_bonuses += bon

        attendance_rows.append({
            "teacher": t,
            "attendance": att,
            "status": status,
            "check_in": att.check_in.strftime("%I:%M %p") if (att and att.check_in) else "---",
            "check_out": att.check_out.strftime("%I:%M %p") if (att and att.check_out) else "---",
            "late_minutes": att.late_minutes if att else 0,
            "deduction": ded,
            "bonus": bon,
            "remarks": att.remarks if att else "",
            "method": att.attendance_method if att else "---",
        })

    context = {
        "target_date": target_date,
        "setting": setting,
        "school_setting": school_setting,
        "attendance_rows": attendance_rows,
        "total_staff": len(teachers),
        "present_count": present_cnt,
        "late_count": late_cnt,
        "absent_count": absent_cnt,
        "half_day_count": half_day_cnt,
        "leave_count": leave_cnt,
        "holiday_count": holiday_cnt,
        "total_deductions": total_deductions,
        "total_bonuses": total_bonuses,
    }
    return render(request, "teachers/daily_attendance_print.html", context)


@login_required
def biometric_fingerprint_import(request):
    """
    Import punch logs from Biometric / Fingerprint machine via file upload or pasting logs.
    """
    setting = TeacherAttendanceSetting.get_settings()
    if request.method == "POST":
        form = BiometricImportForm(request.POST, request.FILES)
        if form.is_valid():
            override_date = form.cleaned_data.get("attendance_date")
            paste_data = form.cleaned_data.get("paste_data", "")
            upload_file = request.FILES.get("import_file")

            lines_to_process = []
            if paste_data.strip():
                lines_to_process.extend(paste_data.strip().splitlines())

            if upload_file:
                fname = upload_file.name.lower()
                if fname.endswith((".xlsx", ".xls")):
                    import openpyxl
                    wb = openpyxl.load_workbook(upload_file, data_only=True)
                    ws = wb.active
                    for row in ws.iter_rows(values_only=True):
                        if not any(row):
                            continue
                        row_strs = [str(c or "").strip() for c in row]
                        lines_to_process.append(",".join(row_strs))
                else:
                    content = upload_file.read().decode("utf-8", errors="ignore")
                    lines_to_process.extend(content.splitlines())

            imported_count = 0
            errors = []
            with transaction.atomic():
                for line_idx, line in enumerate(lines_to_process, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    delims = [",", "\t", ";"]
                    parts = []
                    for d in delims:
                        if d in line:
                            parts = [p.strip() for p in line.split(d)]
                            break
                    if not parts:
                        parts = [p.strip() for p in line.split()]

                    if not parts or len(parts) < 2:
                        continue

                    staff_code = parts[0]
                    if "KMS-STAFF:" in staff_code.upper():
                        staff_code = staff_code.split(":", 1)[1].strip()

                    teacher = Teacher.objects.filter(
                        Q(teacher_id__iexact=staff_code) | Q(full_name__iexact=staff_code)
                    ).first()

                    if not teacher:
                        errors.append(f"Line {line_idx}: Staff ID '{staff_code}' not found.")
                        continue

                    rec_date = override_date
                    in_time = None
                    out_time = None
                    idx = 1

                    if len(parts) >= 3 and any(char in parts[1] for char in ["-", "/"]):
                        try:
                            d_str = parts[1].replace("/", "-")
                            p_date = datetime.strptime(d_str, "%Y-%m-%d").date()
                            rec_date = p_date
                            idx = 2
                        except ValueError:
                            try:
                                p_date = datetime.strptime(parts[1], "%d-%m-%Y").date()
                                rec_date = p_date
                                idx = 2
                            except ValueError:
                                pass

                    if not rec_date:
                        rec_date = timezone.localtime(timezone.now()).date()

                    if len(parts) > idx:
                        t1_str = parts[idx]
                        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M%p"):
                            try:
                                in_time = datetime.strptime(t1_str, fmt).time()
                                break
                            except ValueError:
                                pass
                        idx += 1

                    if len(parts) > idx:
                        t2_str = parts[idx]
                        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M%p"):
                            try:
                                out_time = datetime.strptime(t2_str, fmt).time()
                                break
                            except ValueError:
                                pass

                    att, _ = TeacherAttendance.objects.get_or_create(
                        teacher=teacher,
                        date=rec_date,
                        defaults={
                            "attendance_method": "Fingerprint",
                            "status": "Present",
                        }
                    )
                    att.attendance_method = "Fingerprint"
                    if in_time:
                        att.check_in = in_time
                    if out_time:
                        att.check_out = out_time
                    att.calculate_and_apply_deduction(setting)
                    att.save()
                    imported_count += 1

            if imported_count > 0:
                messages.success(request, f"Successfully processed {imported_count} biometric / fingerprint attendance records.")
            if errors:
                messages.warning(request, f"Some records were skipped: {'; '.join(errors[:4])}")
            return redirect("qr_attendance_scan")
    else:
        form = BiometricImportForm(initial={"attendance_date": timezone.localtime(timezone.now()).date()})

    return render(request, "teachers/biometric_import.html", {"form": form, "setting": setting})


@login_required
def monthly_attendance_sheet(request):
    """
    Complete Monthly Teacher Attendance & Salary Cutting Sheet (Image B requirement).
    Displays day-by-day matrix (1-31), late cuts, absent cuts, bonuses, and net payable.
    """
    today = timezone.localtime(timezone.now()).date()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    setting = TeacherAttendanceSetting.get_settings()

    num_days = calendar.monthrange(year, month)[1]
    days_range = list(range(1, num_days + 1))

    day_headers = []
    for d in days_range:
        cur_d = date(year, month, d)
        day_headers.append({
            "day": d,
            "weekday": cur_d.strftime("%a"),
            "is_sunday": cur_d.weekday() == 6,
        })

    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")

    attendances = TeacherAttendance.objects.filter(
        date__year=year,
        date__month=month,
    ).select_related("teacher")

    att_map = {}
    for a in attendances:
        att_map[(a.teacher_id, a.date.day)] = a

    sheet_rows = []
    grand_totals = {
        "present": 0,
        "late": 0,
        "absent": 0,
        "half_day": 0,
        "leave": 0,
        "late_mins": 0,
        "late_deductions": Decimal("0.00"),
        "absent_deductions": Decimal("0.00"),
        "total_deductions": Decimal("0.00"),
        "bonuses": Decimal("0.00"),
        "gross_salary": Decimal("0.00"),
        "net_salary": Decimal("0.00"),
    }

    for t in teachers:
        day_cells = []
        p_cnt = 0
        l_cnt = 0
        a_cnt = 0
        hd_cnt = 0
        lv_cnt = 0
        late_mins = 0
        late_ded = Decimal("0.00")
        absent_ded = Decimal("0.00")
        bonuses = Decimal("0.00")

        base_pay = t.salary_scale.basic_pay if (t.salary_scale and t.salary_scale.basic_pay) else Decimal("0.00")
        allowances = t.salary_scale.total_allowances if t.salary_scale else Decimal("0.00")
        gross = base_pay + allowances

        for d in days_range:
            att = att_map.get((t.pk, d))
            cur_d = date(year, month, d)
            is_sun = cur_d.weekday() == 6

            if att:
                status = att.status
                badge = "P"
                badge_class = "bg-success"
                if status == "Late":
                    badge = "L"
                    badge_class = "bg-warning text-dark"
                    l_cnt += 1
                    late_mins += att.late_minutes
                    late_ded += att.deduction_amount
                elif status == "Absent":
                    badge = "A"
                    badge_class = "bg-danger"
                    a_cnt += 1
                    absent_ded += att.deduction_amount
                elif status == "Half Day":
                    badge = "HD"
                    badge_class = "bg-info text-dark"
                    hd_cnt += 1
                    absent_ded += att.deduction_amount
                elif status == "Leave":
                    badge = "LV"
                    badge_class = "bg-secondary"
                    lv_cnt += 1
                elif status == "Holiday":
                    badge = "H"
                    badge_class = "bg-light text-muted border"
                else:
                    p_cnt += 1

                bonuses += att.bonus_amount
                day_cells.append({
                    "day": d,
                    "record": att,
                    "badge": badge,
                    "badge_class": badge_class,
                    "status": status,
                    "in_time": att.check_in.strftime("%H:%M") if att.check_in else "",
                    "deduction": att.deduction_amount,
                })
            else:
                if is_sun:
                    day_cells.append({
                        "day": d,
                        "record": None,
                        "badge": "Off",
                        "badge_class": "bg-light text-muted border",
                        "status": "Sunday",
                    })
                else:
                    day_cells.append({
                        "day": d,
                        "record": None,
                        "badge": "-",
                        "badge_class": "text-muted",
                        "status": "Unmarked",
                    })

        total_ded = late_ded + absent_ded
        net_estimated = max(Decimal("0.00"), gross + bonuses - total_ded)

        grand_totals["present"] += p_cnt
        grand_totals["late"] += l_cnt
        grand_totals["absent"] += a_cnt
        grand_totals["half_day"] += hd_cnt
        grand_totals["leave"] += lv_cnt
        grand_totals["late_mins"] += late_mins
        grand_totals["late_deductions"] += late_ded
        grand_totals["absent_deductions"] += absent_ded
        grand_totals["total_deductions"] += total_ded
        grand_totals["bonuses"] += bonuses
        grand_totals["gross_salary"] += gross
        grand_totals["net_salary"] += net_estimated

        sheet_rows.append({
            "teacher": t,
            "day_cells": day_cells,
            "present_count": p_cnt,
            "late_count": l_cnt,
            "absent_count": a_cnt,
            "half_day_count": hd_cnt,
            "leave_count": lv_cnt,
            "late_mins": late_mins,
            "late_hours": round(late_mins / 60, 1),
            "late_deductions": late_ded,
            "absent_deductions": absent_ded,
            "total_deductions": total_ded,
            "bonuses": bonuses,
            "gross_salary": gross,
            "net_salary": net_estimated,
        })

    month_name = calendar.month_name[month]
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        "month": month,
        "year": year,
        "month_name": month_name,
        "months": months,
        "years": range(2024, 2031),
        "days_range": days_range,
        "day_headers": day_headers,
        "sheet_rows": sheet_rows,
        "grand_totals": grand_totals,
        "setting": setting,
        "school_setting": SchoolSetting.objects.first(),
    }

    if request.GET.get("print") == "1":
        return render(request, "teachers/monthly_attendance_print.html", context)

    return render(request, "teachers/monthly_attendance_sheet.html", context)


@login_required
def monthly_attendance_print(request):
    """
    Printable / PDF Monthly Faculty Attendance Sheet for Principal, Vice Principal & Office.
    """
    req_copy = request.GET.copy()
    req_copy["print"] = "1"
    request.GET = req_copy
    return monthly_attendance_sheet(request)


@login_required
def export_monthly_attendance_excel(request):
    """
    Export complete monthly teacher attendance and salary sheet to Excel.
    """
    today = timezone.localtime(timezone.now()).date()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    num_days = calendar.monthrange(year, month)[1]
    days_range = list(range(1, num_days + 1))

    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")
    attendances = TeacherAttendance.objects.filter(date__year=year, date__month=month)

    att_map = {}
    for a in attendances:
        att_map[(a.teacher_id, a.date.day)] = a

    headers = ["Staff ID", "Teacher Name", "Designation", "Base Pay (PKR)"]
    for d in days_range:
        headers.append(f"Day {d}")

    headers.extend([
        "Present Days",
        "Late Days",
        "Absent Days",
        "Half Days",
        "Late Hours",
        "Late Cuts (PKR)",
        "Absent Cuts (PKR)",
        "Total Cuts (PKR)",
        "Bonus (PKR)",
        "Net Payable (PKR)",
    ])

    rows = []
    for t in teachers:
        base_pay = t.salary_scale.basic_pay if (t.salary_scale and t.salary_scale.basic_pay) else Decimal("0.00")
        allowances = t.salary_scale.total_allowances if t.salary_scale else Decimal("0.00")
        gross = base_pay + allowances

        row = [t.teacher_id, t.full_name, t.designation, float(base_pay)]

        p_cnt = 0
        l_cnt = 0
        a_cnt = 0
        hd_cnt = 0
        late_mins = 0
        late_ded = Decimal("0.00")
        absent_ded = Decimal("0.00")
        bonuses = Decimal("0.00")

        for d in days_range:
            att = att_map.get((t.pk, d))
            if att:
                status = att.status
                if status == "Late":
                    row.append(f"L ({att.check_in.strftime('%H:%M') if att.check_in else ''})")
                    l_cnt += 1
                    late_mins += att.late_minutes
                    late_ded += att.deduction_amount
                elif status == "Absent":
                    row.append("A")
                    a_cnt += 1
                    absent_ded += att.deduction_amount
                elif status == "Half Day":
                    row.append("HD")
                    hd_cnt += 1
                    absent_ded += att.deduction_amount
                elif status == "Leave":
                    row.append("LV")
                elif status == "Holiday":
                    row.append("H")
                else:
                    row.append("P")
                    p_cnt += 1
                bonuses += att.bonus_amount
            else:
                cur_d = date(year, month, d)
                row.append("Off" if cur_d.weekday() == 6 else "-")

        total_ded = late_ded + absent_ded
        net_payable = max(Decimal("0.00"), gross + bonuses - total_ded)

        row.extend([
            p_cnt,
            l_cnt,
            a_cnt,
            hd_cnt,
            round(late_mins / 60, 2),
            float(late_ded),
            float(absent_ded),
            float(total_ded),
            float(bonuses),
            float(net_payable),
        ])
        rows.append(row)

    month_name = calendar.month_name[month]
    buffer = create_styled_workbook(f"Attendance {month_name} {year}", headers, rows)
    return excel_download_response(buffer, f"KMS_Teacher_Attendance_{month_name}_{year}.xlsx")


@login_required
def yearly_attendance_sheet(request):
    """
    Full 12-Month Yearly Teacher Attendance & Salary Cutting Sheet (Image B requirement).
    """
    today = timezone.localtime(timezone.now()).date()
    year = int(request.GET.get("year", today.year))
    setting = TeacherAttendanceSetting.get_settings()

    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")
    attendances = TeacherAttendance.objects.filter(date__year=year)

    # Group by (teacher_id, month)
    att_by_month = {}
    for a in attendances:
        key = (a.teacher_id, a.date.month)
        if key not in att_by_month:
            att_by_month[key] = {
                "present": 0, "late": 0, "absent": 0, "half_day": 0,
                "late_ded": Decimal("0.00"), "absent_ded": Decimal("0.00"), "bonus": Decimal("0.00"),
            }
        rec = att_by_month[key]
        if a.status == "Present":
            rec["present"] += 1
        elif a.status == "Late":
            rec["late"] += 1
            rec["late_ded"] += a.deduction_amount
        elif a.status == "Absent":
            rec["absent"] += 1
            rec["absent_ded"] += a.deduction_amount
        elif a.status == "Half Day":
            rec["half_day"] += 1
            rec["absent_ded"] += a.deduction_amount
        rec["bonus"] += a.bonus_amount

    months_info = [(m, calendar.month_abbr[m]) for m in range(1, 13)]

    sheet_rows = []
    for t in teachers:
        month_data = []
        tot_p = 0
        tot_l = 0
        tot_a = 0
        tot_late_ded = Decimal("0.00")
        tot_abs_ded = Decimal("0.00")
        tot_bonus = Decimal("0.00")

        base_pay = t.salary_scale.basic_pay if (t.salary_scale and t.salary_scale.basic_pay) else Decimal("0.00")
        allowances = t.salary_scale.total_allowances if t.salary_scale else Decimal("0.00")
        monthly_gross = base_pay + allowances

        for m_num, m_name in months_info:
            data = att_by_month.get((t.pk, m_num), {
                "present": 0, "late": 0, "absent": 0, "half_day": 0,
                "late_ded": Decimal("0.00"), "absent_ded": Decimal("0.00"), "bonus": Decimal("0.00"),
            })
            m_total_ded = data["late_ded"] + data["absent_ded"]
            month_data.append({
                "month_num": m_num,
                "present": data["present"],
                "late": data["late"],
                "absent": data["absent"],
                "half_day": data["half_day"],
                "deductions": m_total_ded,
                "bonus": data["bonus"],
            })
            tot_p += data["present"]
            tot_l += data["late"]
            tot_a += data["absent"]
            tot_late_ded += data["late_ded"]
            tot_abs_ded += data["absent_ded"]
            tot_bonus += data["bonus"]

        tot_ded = tot_late_ded + tot_abs_ded
        annual_gross = monthly_gross * 12
        annual_net = max(Decimal("0.00"), annual_gross + tot_bonus - tot_ded)

        sheet_rows.append({
            "teacher": t,
            "months": month_data,
            "tot_present": tot_p,
            "tot_late": tot_l,
            "tot_absent": tot_a,
            "tot_late_ded": tot_late_ded,
            "tot_abs_ded": tot_abs_ded,
            "tot_ded": tot_ded,
            "tot_bonus": tot_bonus,
            "annual_gross": annual_gross,
            "annual_net": annual_net,
        })

    context = {
        "year": year,
        "years": range(2024, 2031),
        "months_info": months_info,
        "sheet_rows": sheet_rows,
        "setting": setting,
    }
    return render(request, "teachers/yearly_attendance_sheet.html", context)


@login_required
def export_yearly_attendance_excel(request):
    """
    Export yearly teacher attendance and salary cutting sheet to Excel.
    """
    today = timezone.localtime(timezone.now()).date()
    year = int(request.GET.get("year", today.year))

    teachers = Teacher.objects.filter(status="Active").select_related("salary_scale").order_by("teacher_id")
    attendances = TeacherAttendance.objects.filter(date__year=year)

    att_by_month = {}
    for a in attendances:
        key = (a.teacher_id, a.date.month)
        if key not in att_by_month:
            att_by_month[key] = {
                "present": 0, "late": 0, "absent": 0,
                "late_ded": Decimal("0.00"), "absent_ded": Decimal("0.00"), "bonus": Decimal("0.00"),
            }
        rec = att_by_month[key]
        if a.status == "Present":
            rec["present"] += 1
        elif a.status == "Late":
            rec["late"] += 1
            rec["late_ded"] += a.deduction_amount
        elif a.status == "Absent":
            rec["absent"] += 1
            rec["absent_ded"] += a.deduction_amount
        elif a.status == "Half Day":
            rec["absent_ded"] += a.deduction_amount
        rec["bonus"] += a.bonus_amount

    headers = ["Staff ID", "Teacher Name", "Designation", "Base Pay (PKR)"]
    for m in range(1, 13):
        headers.append(f"{calendar.month_abbr[m]} (P/L/A)")

    headers.extend([
        "Annual Present",
        "Annual Late",
        "Annual Absent",
        "Annual Late Cuts (PKR)",
        "Annual Absent Cuts (PKR)",
        "Total Annual Cuts (PKR)",
        "Annual Bonuses (PKR)",
        "Annual Estimated Net (PKR)",
    ])

    rows = []
    for t in teachers:
        base_pay = t.salary_scale.basic_pay if (t.salary_scale and t.salary_scale.basic_pay) else Decimal("0.00")
        allowances = t.salary_scale.total_allowances if t.salary_scale else Decimal("0.00")
        monthly_gross = base_pay + allowances

        row = [t.teacher_id, t.full_name, t.designation, float(base_pay)]

        tot_p = 0
        tot_l = 0
        tot_a = 0
        tot_late_ded = Decimal("0.00")
        tot_abs_ded = Decimal("0.00")
        tot_bonus = Decimal("0.00")

        for m in range(1, 13):
            data = att_by_month.get((t.pk, m), {"present": 0, "late": 0, "absent": 0, "late_ded": Decimal("0.00"), "absent_ded": Decimal("0.00"), "bonus": Decimal("0.00")})
            row.append(f"{data['present']}/{data['late']}/{data['absent']}")
            tot_p += data["present"]
            tot_l += data["late"]
            tot_a += data["absent"]
            tot_late_ded += data["late_ded"]
            tot_abs_ded += data["absent_ded"]
            tot_bonus += data["bonus"]

        tot_ded = tot_late_ded + tot_abs_ded
        annual_gross = monthly_gross * 12
        annual_net = max(Decimal("0.00"), annual_gross + tot_bonus - tot_ded)

        row.extend([
            tot_p,
            tot_l,
            tot_a,
            float(tot_late_ded),
            float(tot_abs_ded),
            float(tot_ded),
            float(tot_bonus),
            float(annual_net),
        ])
        rows.append(row)

    buffer = create_styled_workbook(f"Yearly Sheet {year}", headers, rows)
    return excel_download_response(buffer, f"KMS_Yearly_Teacher_Attendance_{year}.xlsx")


@login_required
def attendance_settings_view(request):
    """
    Configure Shift Timing (e.g. 08:00 AM to 12:30 PM), Grace Period,
    and Hourly / Daily Salary Cutting policies.
    """
    setting = TeacherAttendanceSetting.get_settings()
    if request.method == "POST":
        form = TeacherAttendanceSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher attendance & salary cutting settings updated successfully.")
            return redirect("attendance_settings")
    else:
        form = TeacherAttendanceSettingForm(instance=setting)

    return render(request, "teachers/attendance_settings.html", {"form": form, "setting": setting})


@login_required
def all_staff_qr_cards(request):
    """
    Printable batch sheet of Staff QR Badges / Attendance Cards for scanning terminal.
    """
    teachers = Teacher.objects.filter(status="Active").order_by("teacher_id")
    school_setting = SchoolSetting.objects.first()
    return render(
        request,
        "teachers/staff_qr_cards_bulk.html",
        {"teachers": teachers, "school_setting": school_setting},
    )


@login_required
def sync_salary_bill_attendance_view(request, pk):
    """
    One-click re-sync of an individual MonthlySalaryBill from TeacherAttendance records.
    """
    bill = get_object_or_404(MonthlySalaryBill, pk=pk)
    if bill.sync_from_attendance():
        messages.success(
            request,
            f"Salary bill for {bill.teacher.full_name} ({bill.month_name} {bill.year}) was successfully re-calculated from attendance records.",
        )
    else:
        messages.warning(
            request,
            f"No attendance records found for {bill.teacher.full_name} in {bill.month_name} {bill.year}.",
        )
    return redirect("salary_bill_detail", pk=bill.pk)


