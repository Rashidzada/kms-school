from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from school.models import AcademicSession, ClassLevel, Section
from students.models import FamilyHousehold, Student
from .forms import FamilyFeePaymentForm, FeeAdjustmentForm, FeeCollectForm
from .models import FeePaymentReceipt, StudentFeeLedger, StudentFeeMonthEntry
from .utils import initialize_ledger_months, recalculate_ledger_arrears


@login_required
def fee_register(request):
    """
    Fee Register grid view (FR-5.3):
    Rows = active students, Columns = 12 months, filterable by session and class.
    """
    active_session = AcademicSession.objects.filter(is_active=True).first()
    session_id = request.GET.get("session")
    if session_id:
        current_session = get_object_or_404(AcademicSession, pk=session_id)
    else:
        current_session = active_session or AcademicSession.objects.first()

    class_id = request.GET.get("class", "")
    students = Student.objects.filter(status="Active").select_related("current_class", "current_section")
    if class_id:
        students = students.filter(current_class_id=class_id)

    # Ensure each student has a ledger for this session
    student_rows = []
    if current_session:
        for student in students:
            ledger, created = StudentFeeLedger.objects.get_or_create(
                student=student, academic_session=current_session
            )
            if created:
                initialize_ledger_months(
                    ledger, student, student.current_class.monthly_fee if student.current_class else Decimal("0.00")
                )
            entries = {e.month: e for e in ledger.monthly_entries.all()}
            total_due = sum(e.total_amount for e in entries.values())
            total_paid = sum(e.paid_amount for e in entries.values())
            total_balance = sum(e.balance for e in entries.values())
            student_rows.append({
                "student": student,
                "ledger": ledger,
                "entries": entries,
                "total_due": total_due,
                "total_paid": total_paid,
                "total_balance": total_balance,
            })

    classes = ClassLevel.objects.all()
    sessions = AcademicSession.objects.all()

    context = {
        "student_rows": student_rows,
        "current_session": current_session,
        "classes": classes,
        "sessions": sessions,
        "selected_class": class_id,
        "months": range(1, 13),
    }
    return render(request, "finance/fee_register.html", context)


@login_required
def collect_fee(request, student_id):
    """
    Collect Fee screen per student (FR-5.4, FR-5.5, FR-5.6, FR-5.7).
    Lump-sum allocated across oldest unpaid months first, auto receipt #, arrears recalculated.
    """
    student = get_object_or_404(Student, pk=student_id)
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    ledger, created = StudentFeeLedger.objects.get_or_create(
        student=student, academic_session=active_session
    )
    if created:
        initialize_ledger_months(
            ledger, student, student.current_class.monthly_fee if student.current_class else Decimal("0.00")
        )

    if request.method == "POST":
        form = FeeCollectForm(ledger, request.POST)
        if form.is_valid():
            selected_months = list(form.cleaned_data["selected_months"].order_by("month"))
            amount_paid = form.cleaned_data["amount_paid"]
            payment_date = form.cleaned_data["payment_date"]
            remarks = form.cleaned_data["remarks"]

            total_outstanding = sum(m.balance for m in selected_months)

            if amount_paid <= 0:
                messages.error(request, "Amount paid must be greater than zero.")
            elif amount_paid > total_outstanding:
                messages.error(
                    request,
                    f"Amount paid ({amount_paid}) cannot exceed total outstanding balance of selected months ({total_outstanding}).",
                )
            else:
                with transaction.atomic():
                    receipt = FeePaymentReceipt.objects.create(
                        payment_date=payment_date,
                        amount_paid=amount_paid,
                        student=student,
                        remarks=remarks,
                    )

                    remaining = amount_paid
                    for entry in selected_months:
                        if remaining <= 0:
                            break
                        due = entry.balance
                        pay = min(due, remaining)
                        entry.paid_amount += pay
                        entry.last_payment_date = payment_date
                        entry.last_receipt_no = receipt.receipt_no
                        entry.save(update_fields=["paid_amount", "last_payment_date", "last_receipt_no"])
                        receipt.month_entries.add(entry)
                        remaining -= pay

                    if remaining > 0:
                        receipt.remarks = f"{receipt.remarks} [Unallocated: {remaining}]".strip()
                        receipt.save(update_fields=["remarks"])

                    recalculate_ledger_arrears(ledger)

                messages.success(request, f"Fee payment recorded with Receipt No. {receipt.receipt_no}.")
                return redirect("fee_receipt", pk=receipt.pk)
    else:
        form = FeeCollectForm(
            ledger,
            initial={"payment_date": timezone.now().date()},
        )

    unpaid_entries = ledger.monthly_entries.filter(is_paid=False).order_by("month")
    return render(
        request,
        "finance/collect_fee.html",
        {"student": student, "ledger": ledger, "form": form, "unpaid_entries": unpaid_entries},
    )


@login_required
def family_payment(request, household_id):
    """
    Family Payment screen (FR-5.8):
    Pay across selected month entries belonging to any linked sibling students in one receipt.
    """
    family = get_object_or_404(FamilyHousehold, pk=household_id)
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    if request.method == "POST":
        form = FamilyFeePaymentForm(family, active_session, request.POST)
        if form.is_valid():
            selected_months = list(form.cleaned_data["selected_months"].order_by("month"))
            amount_paid = form.cleaned_data["amount_paid"]
            payment_date = form.cleaned_data["payment_date"]
            remarks = form.cleaned_data["remarks"]

            total_outstanding = sum(m.balance for m in selected_months)
            if amount_paid <= 0:
                messages.error(request, "Amount paid must be greater than zero.")
            elif amount_paid > total_outstanding:
                messages.error(
                    request,
                    f"Amount paid ({amount_paid}) cannot exceed total outstanding balance of selected months ({total_outstanding}).",
                )
            else:
                first_student = family.students.filter(status="Active").first()
                if not first_student:
                    messages.error(request, "No active students found in this family.")
                    return redirect("family_list")

                with transaction.atomic():
                    combined_remarks = f"Family Payment: {family.family_id} ({family.father_guardian_name}). {remarks}".strip()
                    receipt = FeePaymentReceipt.objects.create(
                        payment_date=payment_date,
                        amount_paid=amount_paid,
                        student=first_student,
                        remarks=combined_remarks,
                    )

                    remaining = amount_paid
                    affected_ledgers = set()
                    for entry in selected_months:
                        if remaining <= 0:
                            break
                        due = entry.balance
                        pay = min(due, remaining)
                        entry.paid_amount += pay
                        entry.last_payment_date = payment_date
                        entry.last_receipt_no = receipt.receipt_no
                        entry.save(update_fields=["paid_amount", "last_payment_date", "last_receipt_no"])
                        receipt.month_entries.add(entry)
                        affected_ledgers.add(entry.ledger)
                        remaining -= pay

                    if remaining > 0:
                        receipt.remarks = f"{receipt.remarks} [Unallocated: {remaining}]".strip()
                        receipt.save(update_fields=["remarks"])

                    for ledg in affected_ledgers:
                        recalculate_ledger_arrears(ledg)

                messages.success(request, f"Family payment recorded with Receipt No. {receipt.receipt_no}.")
                return redirect("fee_receipt", pk=receipt.pk)
    else:
        form = FamilyFeePaymentForm(
            family,
            active_session,
            initial={"payment_date": timezone.now().date()},
        )

    return render(
        request,
        "finance/family_payment.html",
        {"family": family, "form": form, "active_session": active_session},
    )


@login_required
def fee_adjust(request, student_id):
    """
    Fee Adjustment screen per student (FR-5.10):
    Allows changing monthly fee going forward, and/or editing exam fee / other charges for a month.
    """
    student = get_object_or_404(Student, pk=student_id)
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    ledger = get_object_or_404(StudentFeeLedger, student=student, academic_session=active_session)

    if request.method == "POST":
        form = FeeAdjustmentForm(request.POST)
        if form.is_valid():
            from_month = int(form.cleaned_data["from_month"])
            new_fee = form.cleaned_data.get("new_monthly_fee")
            single_month = form.cleaned_data.get("single_month")
            exam_fee = form.cleaned_data.get("exam_fee") or Decimal("0.00")
            other_charges = form.cleaned_data.get("other_charges") or Decimal("0.00")

            with transaction.atomic():
                # Apply new monthly fee to from_month and subsequent months
                if new_fee is not None:
                    ledger.monthly_entries.filter(month__gte=from_month).update(monthly_fee=new_fee)

                # Edit exam fee / other charges for single specific month
                if single_month:
                    target_m = int(single_month)
                    entry = ledger.monthly_entries.filter(month=target_m).first()
                    if entry:
                        entry.exam_fee = exam_fee
                        entry.other_charges = other_charges
                        entry.save(update_fields=["exam_fee", "other_charges"])

                recalculate_ledger_arrears(ledger)

            messages.success(request, f"Fee adjustments applied for {student.full_name}.")
            return redirect("student_detail", pk=student.pk)
    else:
        form = FeeAdjustmentForm()

    return render(
        request,
        "finance/fee_adjust.html",
        {"student": student, "ledger": ledger, "form": form},
    )


@login_required
def fee_receipt(request, pk):
    """
    Printable Fee Receipt view (FR-5.9, FR-8.4).
    """
    receipt = get_object_or_404(
        FeePaymentReceipt.objects.select_related("student", "student__current_class"),
        pk=pk,
    )
    month_entries = receipt.month_entries.select_related("ledger", "ledger__student").order_by("month")
    return render(
        request,
        "finance/fee_receipt.html",
        {"receipt": receipt, "month_entries": month_entries},
    )


@login_required
def defaulters_list(request):
    """
    Defaulters List (FR-5.11):
    Active students with positive outstanding balance for the active session.
    """
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")

    students = Student.objects.filter(status="Active").select_related("current_class", "current_section")
    if class_id:
        students = students.filter(current_class_id=class_id)
    if section_id:
        students = students.filter(current_section_id=section_id)

    defaulters = []
    total_school_dues = Decimal("0.00")

    if active_session:
        for s in students:
            ledger = StudentFeeLedger.objects.filter(student=s, academic_session=active_session).first()
            if ledger:
                unpaid_entries = [e for e in ledger.monthly_entries.all() if e.balance > 0]
                if unpaid_entries:
                    student_dues = sum(e.balance for e in unpaid_entries)
                    total_school_dues += student_dues
                    defaulters.append({
                        "student": s,
                        "unpaid_months_count": len(unpaid_entries),
                        "total_dues": student_dues,
                        "unpaid_entries": unpaid_entries,
                    })

    # Sort highest-due first
    defaulters.sort(key=lambda x: x["total_dues"], reverse=True)

    classes = ClassLevel.objects.all()
    sections = Section.objects.all()

    context = {
        "defaulters": defaulters,
        "total_school_dues": total_school_dues,
        "classes": classes,
        "sections": sections,
        "selected_class": class_id,
        "selected_section": section_id,
        "active_session": active_session,
    }
    return render(request, "finance/defaulters_list.html", context)


@login_required
def family_dues(request):
    """
    Family Dues summary (FR-5.12):
    Total outstanding balance per family household across its students in active session, sorted highest-due first.
    """
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    families = FamilyHousehold.objects.prefetch_related("students").all()

    family_records = []
    grand_total_family_dues = Decimal("0.00")

    for fam in families:
        fam_students = fam.students.filter(status="Active")
        fam_dues = Decimal("0.00")
        unpaid_count = 0
        for s in fam_students:
            if active_session:
                ledger = StudentFeeLedger.objects.filter(student=s, academic_session=active_session).first()
                if ledger:
                    for e in ledger.monthly_entries.all():
                        if e.balance > 0:
                            fam_dues += e.balance
                            unpaid_count += 1

        grand_total_family_dues += fam_dues
        family_records.append({
            "family": fam,
            "students": fam_students,
            "total_dues": fam_dues,
            "unpaid_count": unpaid_count,
        })

    family_records.sort(key=lambda x: x["total_dues"], reverse=True)

    context = {
        "family_records": family_records,
        "grand_total_family_dues": grand_total_family_dues,
        "active_session": active_session,
    }
    return render(request, "finance/family_dues.html", context)


@login_required
def class_fee_summary(request):
    """
    Class Fee Summary report (FR-5.13):
    For every class level: total due, total paid, and outstanding balance for active session.
    """
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    classes = ClassLevel.objects.all()

    summary = []
    grand_due = Decimal("0.00")
    grand_paid = Decimal("0.00")
    grand_balance = Decimal("0.00")

    for cls in classes:
        students = Student.objects.filter(current_class=cls, status="Active")
        cls_due = Decimal("0.00")
        cls_paid = Decimal("0.00")
        cls_balance = Decimal("0.00")

        if active_session:
            ledgers = StudentFeeLedger.objects.filter(
                student__in=students, academic_session=active_session
            ).prefetch_related("monthly_entries")

            for l in ledgers:
                for e in l.monthly_entries.all():
                    cls_due += e.total_amount
                    cls_paid += e.paid_amount
                    cls_balance += e.balance

        grand_due += cls_due
        grand_paid += cls_paid
        grand_balance += cls_balance

        summary.append({
            "class": cls,
            "student_count": students.count(),
            "total_due": cls_due,
            "total_paid": cls_paid,
            "balance": cls_balance,
        })

    context = {
        "summary": summary,
        "grand_due": grand_due,
        "grand_paid": grand_paid,
        "grand_balance": grand_balance,
        "active_session": active_session,
    }
    return render(request, "finance/class_fee_summary.html", context)
