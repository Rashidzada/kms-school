from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from finance.models import StudentFeeLedger
from finance.utils import apply_withdrawal_stop, initialize_ledger_months, roll_over_arrears
from school.models import AcademicSession, ClassLevel, Section
from school.whatsapp_utils import build_student_dues_reminder_msg
from .forms import FamilyHouseholdForm, SinglePromoteForm, StudentForm, StudentWithdrawForm
from .models import FamilyHousehold, PromotionHistory, Student


def compute_students_fee_ledger_map(students_list, active_session=None):
    """
    Computes fee status, paid months (real names), pending months with dues,
    and full family household dues for a given list of students.
    Zero N+1 queries by bulk-prefetching ledgers and monthly entries.
    """
    if not active_session:
        active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    student_ids = [s.id for s in students_list]
    ledgers = StudentFeeLedger.objects.filter(
        student_id__in=student_ids,
        academic_session=active_session
    ).prefetch_related("monthly_entries")
    ledger_map = {l.student_id: l for l in ledgers}

    # Family dues map across all families in this student cohort
    family_ids = set([s.family_id for s in students_list if s.family_id])
    family_dues_map = {fid: Decimal("0.00") for fid in family_ids}
    family_count_map = {fid: 0 for fid in family_ids}

    if family_ids and active_session:
        fam_students = list(Student.objects.filter(family_id__in=family_ids, status="Active").values_list("id", "family_id"))
        fam_student_ids = [fs[0] for fs in fam_students]
        fam_student_to_family = dict(fam_students)

        fam_ledgers = StudentFeeLedger.objects.filter(
            student_id__in=fam_student_ids,
            academic_session=active_session
        ).prefetch_related("monthly_entries")

        for fl in fam_ledgers:
            fl_entries = list(fl.monthly_entries.order_by("month"))
            fl_due = max(Decimal("0.00"), fl_entries[-1].balance if fl_entries else Decimal("0.00"))
            if fl_due > 0:
                fid = fam_student_to_family.get(fl.student_id)
                if fid:
                    family_dues_map[fid] = family_dues_map.get(fid, Decimal("0.00")) + fl_due

        for _, fid in fam_students:
            family_count_map[fid] = family_count_map.get(fid, 0) + 1

    for s in students_list:
        l = ledger_map.get(s.id)
        if not l:
            s.total_dues = Decimal("0.00")
            s.has_dues = False
            s.paid_months_list = []
            s.paid_months_display = "None"
            s.pending_months_list = []
            s.pending_months_display = "None"
            s.family_total_dues = Decimal("0.00")
            s.family_siblings_count = 0
            continue

        entries = list(l.monthly_entries.order_by("month"))
        paid_months = []
        pending_months = []

        for e in entries:
            chg = (e.monthly_fee or Decimal("0.00")) + (e.exam_fee or Decimal("0.00")) + (e.other_charges or Decimal("0.00"))
            if e.month == 1:
                chg += (e.arrears or Decimal("0.00"))
            if chg <= 0 and (e.paid_amount or Decimal("0.00")) <= 0:
                continue
            net_unpaid = chg - (e.paid_amount or Decimal("0.00"))
            if net_unpaid <= 0:
                paid_months.append(e.get_month_display())
            else:
                pending_months.append({
                    "month": e.month,
                    "month_name": e.get_month_display(),
                    "month_abbr": e.month_abbr,
                    "due": net_unpaid,
                })

        tot_due = max(Decimal("0.00"), entries[-1].balance if entries else Decimal("0.00"))

        if len(paid_months) == 12:
            paid_display = "All 12 Months (Jan - Dec)"
        elif len(paid_months) > 3:
            paid_display = f"{paid_months[0]} - {paid_months[-1]} ({len(paid_months)} mos)"
        elif paid_months:
            paid_display = ", ".join(paid_months)
        else:
            paid_display = "No payments yet"

        if pending_months:
            pending_parts = [f"{p['month_name']}: PKR {p['due']:,.0f}" for p in pending_months]
            pending_display = " | ".join(pending_parts)
        else:
            pending_display = "Cleared (PKR 0)"

        s.total_dues = tot_due
        s.has_dues = (tot_due > Decimal("0.00"))
        s.paid_months_list = paid_months
        s.paid_months_display = paid_display
        s.pending_months_list = pending_months
        s.pending_months_display = pending_display
        s.family_total_dues = family_dues_map.get(s.family_id, Decimal("0.00")) if s.family_id else Decimal("0.00")
        s.family_siblings_count = family_count_map.get(s.family_id, 0) if s.family_id else 0

    return students_list


@login_required
def student_list(request):
    """
    Searchable, filterable student list (FR-3.3) with real month dues,
    paid months display, pending dues breakdown, and full family dues:
    Filters: class, section, status, fee_status.
    Free-text search: full name, admission number, father's name, residence.
    """
    students_qs = Student.objects.select_related(
        "current_class", "current_section", "family"
    ).all()

    query = request.GET.get("q", "").strip()
    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")
    status = request.GET.get("status", "")
    fee_status = request.GET.get("fee_status", "")

    if query:
        students_qs = students_qs.filter(
            Q(full_name__icontains=query)
            | Q(admission_no__icontains=query)
            | Q(father_name__icontains=query)
            | Q(residence__icontains=query)
        )

    if class_id:
        students_qs = students_qs.filter(current_class_id=class_id)
    if section_id:
        students_qs = students_qs.filter(current_section_id=section_id)
    if status:
        students_qs = students_qs.filter(status=status)

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    students_list = list(students_qs)
    compute_students_fee_ledger_map(students_list, active_session=active_session)

    # Summary metrics before fee_status filtering
    total_active_students = len([s for s in students_list if s.status == "Active"])
    total_students_with_dues = len([s for s in students_list if s.has_dues])
    total_cleared_students = len([s for s in students_list if not s.has_dues])
    total_outstanding_school_dues = sum(s.total_dues for s in students_list)

    # Filter by fee_status
    if fee_status == "has_dues":
        students_list = [s for s in students_list if s.has_dues]
    elif fee_status == "cleared":
        students_list = [s for s in students_list if not s.has_dues]

    classes = ClassLevel.objects.all()
    sections = Section.objects.all()

    context = {
        "students": students_list,
        "classes": classes,
        "sections": sections,
        "query": query,
        "selected_class": class_id,
        "selected_section": section_id,
        "selected_status": status,
        "selected_fee_status": fee_status,
        "active_session": active_session,
        "total_active_students": total_active_students,
        "total_students_with_dues": total_students_with_dues,
        "total_cleared_students": total_cleared_students,
        "total_outstanding_school_dues": total_outstanding_school_dues,
    }
    return render(request, "students/student_list.html", context)


@login_required
def student_create(request):
    """
    Add a new student (FR-3.1).
    Auto-creates a 12-month fee ledger for the active session (FR-5.1, FR-5.2).
    """
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                student = form.save()
                active_session = AcademicSession.objects.filter(is_active=True).first()
                if active_session:
                    ledger, created = StudentFeeLedger.objects.get_or_create(
                        student=student, academic_session=active_session
                    )
                    if created:
                        initialize_ledger_months(
                            ledger,
                            student,
                            student.current_class.monthly_fee,
                            admission_date=student.admission_date,
                        )
                messages.success(
                    request,
                    f"Student {student.full_name} admitted successfully with Admission No. {student.admission_no}.",
                )
                return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {"form": form, "title": "New Student Admission"})


@login_required
def student_detail(request, pk):
    """
    Student profile detail page (FR-3.4) with fee ledger history, promotion history,
    active session dues left, paid months list, pending months list, and family dues.
    """
    student = get_object_or_404(
        Student.objects.select_related("current_class", "current_section", "family"),
        pk=pk,
    )
    promotions = student.promotions.select_related(
        "from_class", "to_class", "from_section", "to_section"
    ).all()
    ledgers = student.fee_ledgers.select_related("academic_session").prefetch_related(
        "monthly_entries"
    ).all()

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    active_ledger = None
    if active_session:
        active_ledger = ledgers.filter(academic_session=active_session).first()

    student_total_dues = Decimal("0.00")
    paid_months_list = []
    pending_months_list = []
    if active_ledger:
        entries = list(active_ledger.monthly_entries.order_by("month"))
        student_total_dues = max(Decimal("0.00"), entries[-1].balance if entries else Decimal("0.00"))
        for e in entries:
            chg = (e.monthly_fee or Decimal("0.00")) + (e.exam_fee or Decimal("0.00")) + (e.other_charges or Decimal("0.00"))
            if e.month == 1:
                chg += (e.arrears or Decimal("0.00"))
            if chg <= 0 and (e.paid_amount or Decimal("0.00")) <= 0:
                continue
            net_unpaid = chg - (e.paid_amount or Decimal("0.00"))
            if net_unpaid <= 0:
                paid_months_list.append(e.get_month_display())
            else:
                pending_months_list.append({
                    "month": e.month,
                    "month_name": e.get_month_display(),
                    "month_abbr": e.month_abbr,
                    "due": net_unpaid,
                })

    # Full Family / Household Breakdown
    family = student.family
    family_total_dues = Decimal("0.00")
    family_siblings_summary = []
    if family and active_session:
        for sib in family.students.filter(status="Active").select_related("current_class", "current_section"):
            sib_ledger = StudentFeeLedger.objects.filter(student=sib, academic_session=active_session).first()
            if sib_ledger:
                sib_entries = list(sib_ledger.monthly_entries.order_by("month"))
                sib_dues = max(Decimal("0.00"), sib_entries[-1].balance if sib_entries else Decimal("0.00"))
                sib_unpaid = [f"{e.get_month_display()} (PKR {max(Decimal('0.00'), e.total_amount - (e.paid_amount or Decimal('0.00'))):,.0f})" for e in sib_entries if e.balance > 0]
            else:
                sib_dues = Decimal("0.00")
                sib_unpaid = []
            family_total_dues += sib_dues
            family_siblings_summary.append({
                "student": sib,
                "dues": sib_dues,
                "unpaid_months": sib_unpaid,
                "is_current": (sib.id == student.id),
            })

    pending_str = ", ".join([p["month_name"] for p in pending_months_list]) if pending_months_list else "All Cleared"
    whatsapp_data = build_student_dues_reminder_msg(
        student=student,
        student_total_dues=student_total_dues,
        pending_months_summary=pending_str,
        family_total_dues=family_total_dues,
        family_count=len(family_siblings_summary),
    )

    context = {
        "student": student,
        "promotions": promotions,
        "ledgers": ledgers,
        "active_session": active_session,
        "active_ledger": active_ledger,
        "student_total_dues": student_total_dues,
        "paid_months_list": paid_months_list,
        "pending_months_list": pending_months_list,
        "family": family,
        "family_total_dues": family_total_dues,
        "family_siblings_summary": family_siblings_summary,
        "whatsapp_data": whatsapp_data,
    }
    return render(request, "students/student_detail.html", context)


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    old_status = student.status

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            with transaction.atomic():
                updated_student = form.save()
                # If status changed to Inactive (FR-3.5)
                if old_status != "Inactive" and updated_student.status == "Inactive":
                    inactive_date = updated_student.inactive_date or timezone.now().date()
                    updated_student.inactive_date = inactive_date
                    updated_student.save(update_fields=["inactive_date"])
                    apply_withdrawal_stop(updated_student, inactive_date)

                messages.success(request, f"Student {updated_student.full_name} updated successfully.")
                return redirect("student_detail", pk=updated_student.pk)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "students/student_form.html",
        {"form": form, "student": student, "title": f"Edit Student: {student.full_name}"},
    )


@login_required
def student_promote(request, pk):
    """
    Single-student promotion workflow (FR-3.6, FR-3.8, FR-3.9, FR-3.10).
    """
    student = get_object_or_404(Student, pk=pk)
    if student.status == "Withdrawn":
        messages.error(request, "Withdrawn students are not eligible for promotion.")
        return redirect("student_detail", pk=student.pk)

    if request.method == "POST":
        form = SinglePromoteForm(request.POST)
        if form.is_valid():
            to_class = form.cleaned_data["to_class"]
            to_section = form.cleaned_data["to_section"]
            target_session = form.cleaned_data["target_session"]

            with transaction.atomic():
                old_class = student.current_class
                old_section = student.current_section

                # Log promotion history
                PromotionHistory.objects.create(
                    student=student,
                    from_class=old_class,
                    to_class=to_class,
                    from_section=old_section,
                    to_section=to_section,
                    session=target_session.name,
                )

                # Update student
                student.current_class = to_class
                student.current_section = to_section
                student.save(update_fields=["current_class", "current_section"])

                # Auto-create ledger if none exists (FR-3.10)
                ledger, created = StudentFeeLedger.objects.get_or_create(
                    student=student, academic_session=target_session
                )
                if created:
                    initialize_ledger_months(ledger, student, to_class.monthly_fee)
                    # Roll over previous session arrears
                    prev_session = AcademicSession.objects.filter(
                        end_date__lte=target_session.start_date
                    ).order_by("-end_date").first()
                    if prev_session:
                        roll_over_arrears(student, prev_session, target_session)

                messages.success(
                    request,
                    f"{student.full_name} promoted to {to_class.name} - {to_section.name} for session {target_session.name}.",
                )
                return redirect("student_detail", pk=student.pk)
    else:
        active_session = AcademicSession.objects.filter(is_active=True).first()
        form = SinglePromoteForm(initial={"target_session": active_session})

    return render(
        request,
        "students/student_promote.html",
        {"student": student, "form": form},
    )


@login_required
def bulk_promote(request):
    """
    Bulk promotion workflow (FR-3.7, FR-3.8, FR-3.9, FR-3.10):
    Staff select source class + section, view Active students, multi-select,
    and promote together in one transaction.
    """
    classes = ClassLevel.objects.all()
    sections = Section.objects.all()
    sessions = AcademicSession.objects.all()

    source_class_id = request.GET.get("source_class", "")
    source_section_id = request.GET.get("source_section", "")

    students = []
    if source_class_id and source_section_id:
        students = Student.objects.filter(
            current_class_id=source_class_id,
            current_section_id=source_section_id,
            status="Active",
        )

    if request.method == "POST":
        student_ids = request.POST.getlist("selected_students")
        to_class_id = request.POST.get("to_class")
        to_section_id = request.POST.get("to_section")
        target_session_id = request.POST.get("target_session")

        if not student_ids:
            messages.error(request, "No students were selected for promotion.")
        elif not (to_class_id and to_section_id and target_session_id):
            messages.error(request, "Please select destination class, section, and academic session.")
        else:
            to_class = get_object_or_404(ClassLevel, pk=to_class_id)
            to_section = get_object_or_404(Section, pk=to_section_id)
            target_session = get_object_or_404(AcademicSession, pk=target_session_id)

            if to_section.class_level != to_class:
                messages.error(request, "The destination section does not belong to the destination class.")
            else:
                promoted_count = 0
                with transaction.atomic():
                    for s_id in student_ids:
                        s = Student.objects.select_for_update().get(pk=s_id)
                        if s.status == "Withdrawn":
                            continue

                        PromotionHistory.objects.create(
                            student=s,
                            from_class=s.current_class,
                            to_class=to_class,
                            from_section=s.current_section,
                            to_section=to_section,
                            session=target_session.name,
                        )
                        s.current_class = to_class
                        s.current_section = to_section
                        s.save(update_fields=["current_class", "current_section"])

                        ledger, created = StudentFeeLedger.objects.get_or_create(
                            student=s, academic_session=target_session
                        )
                        if created:
                            initialize_ledger_months(ledger, s, to_class.monthly_fee)
                        promoted_count += 1

                messages.success(
                    request,
                    f"Successfully promoted {promoted_count} students to {to_class.name} - {to_section.name}.",
                )
                return redirect("student_list")

    context = {
        "classes": classes,
        "sections": sections,
        "sessions": sessions,
        "source_class_id": source_class_id,
        "source_section_id": source_section_id,
        "students": students,
    }
    return render(request, "students/bulk_promote.html", context)


@login_required
def student_withdraw(request, pk):
    """
    Formal Student Withdrawal workflow (FR-3.11, FR-3.12):
    Captures withdrawal date, class at withdrawal, outstanding arrears, remarks.
    Zeroes out future months and recalculates arrears.
    """
    student = get_object_or_404(Student, pk=pk)

    # Calculate current outstanding arrears across all active session entries
    active_session = AcademicSession.objects.filter(is_active=True).first()
    outstanding = Decimal("0.00")
    if active_session:
        ledger = StudentFeeLedger.objects.filter(
            student=student, academic_session=active_session
        ).first()
        if ledger:
            now_month = timezone.now().month
            for entry in ledger.monthly_entries.filter(month__lte=now_month):
                outstanding += entry.balance

    if request.method == "POST":
        form = StudentWithdrawForm(request.POST, instance=student)
        if form.is_valid():
            with transaction.atomic():
                withdrawn_student = form.save(commit=False)
                withdrawn_student.status = "Withdrawn"
                if not withdrawn_student.withdrawal_date:
                    withdrawn_student.withdrawal_date = timezone.now().date()
                if not withdrawn_student.class_at_withdrawal:
                    withdrawn_student.class_at_withdrawal = f"{student.current_class.name} - {student.current_section.name}"
                withdrawn_student.save()

                apply_withdrawal_stop(withdrawn_student, withdrawn_student.withdrawal_date)

                messages.success(
                    request,
                    f"Student {student.full_name} has been marked Withdrawn as of {withdrawn_student.withdrawal_date}.",
                )
                return redirect("student_detail", pk=student.pk)
    else:
        form = StudentWithdrawForm(
            instance=student,
            initial={
                "withdrawal_date": timezone.now().date(),
                "class_at_withdrawal": f"{student.current_class.name} - {student.current_section.name}",
                "arrears_at_withdrawal": outstanding,
            },
        )

    return render(
        request,
        "students/student_withdraw.html",
        {"student": student, "form": form, "outstanding": outstanding},
    )


@login_required
def family_list(request):
    """
    Searchable family / household list (FR-4.2).
    """
    families = FamilyHousehold.objects.prefetch_related("students").all()
    query = request.GET.get("q", "").strip()
    if query:
        families = families.filter(
            Q(family_id__icontains=query)
            | Q(father_guardian_name__icontains=query)
            | Q(contact_number__icontains=query)
            | Q(address__icontains=query)
        )

    return render(
        request, "students/family_list.html", {"families": families, "query": query}
    )


@login_required
def family_create(request):
    if request.method == "POST":
        form = FamilyHouseholdForm(request.POST)
        if form.is_valid():
            family = form.save()
            messages.success(request, f"Family {family.family_id} created successfully.")
            return redirect("family_list")
    else:
        form = FamilyHouseholdForm()
    return render(request, "students/family_form.html", {"form": form, "title": "Add New Family / Household"})


@login_required
def family_update(request, pk):
    family = get_object_or_404(FamilyHousehold, pk=pk)
    if request.method == "POST":
        form = FamilyHouseholdForm(request.POST, instance=family)
        if form.is_valid():
            form.save()
            messages.success(request, f"Family {family.family_id} updated successfully.")
            return redirect("family_list")
    else:
        form = FamilyHouseholdForm(instance=family)
    return render(
        request,
        "students/family_form.html",
        {"form": form, "family": family, "title": f"Edit Family: {family.family_id}"},
    )


@login_required
def admission_register(request):
    """
    Admission Register (FR-3.13): All students ordered by admission date, printable.
    """
    students = Student.objects.select_related("current_class", "current_section").order_by(
        "admission_date", "admission_no"
    )
    query = request.GET.get("q", "").strip()
    if query:
        students = students.filter(
            Q(full_name__icontains=query)
            | Q(admission_no__icontains=query)
            | Q(father_name__icontains=query)
        )
    return render(
        request,
        "students/admission_register.html",
        {"students": students, "query": query},
    )


@login_required
def withdrawal_register(request):
    """
    Withdrawal Register (FR-3.13): Withdrawn students only, ordered by withdrawal date, printable.
    """
    students = Student.objects.filter(status="Withdrawn").order_by("-withdrawal_date")
    query = request.GET.get("q", "").strip()
    if query:
        students = students.filter(
            Q(full_name__icontains=query)
            | Q(admission_no__icontains=query)
            | Q(class_at_withdrawal__icontains=query)
        )
    return render(
        request,
        "students/withdrawal_register.html",
        {"students": students, "query": query},
    )


@login_required
def school_leaving_certificate(request, pk):
    """
    Printable School Leaving Certificate (SLC) (FR-8.1).
    """
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/slc.html", {"student": student})


@login_required
def character_certificate(request, pk):
    """
    Printable Character Certificate (FR-8.2).
    """
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/character_certificate.html", {"student": student})


@login_required
def export_students_excel(request):
    """
    Export students to professionally styled Excel spreadsheet including
    active session fee status, outstanding dues, paid months, and family dues.
    """
    from school.excel_utils import create_styled_workbook, excel_download_response

    students_qs = Student.objects.select_related(
        "current_class", "current_section", "family"
    ).all()

    # Apply active filters if present
    query = request.GET.get("q", "").strip()
    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")
    status = request.GET.get("status", "")
    fee_status = request.GET.get("fee_status", "")

    if query:
        students_qs = students_qs.filter(
            Q(full_name__icontains=query)
            | Q(admission_no__icontains=query)
            | Q(father_name__icontains=query)
            | Q(residence__icontains=query)
        )
    if class_id:
        students_qs = students_qs.filter(current_class_id=class_id)
    if section_id:
        students_qs = students_qs.filter(current_section_id=section_id)
    if status:
        students_qs = students_qs.filter(status=status)

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    students_list = list(students_qs)
    compute_students_fee_ledger_map(students_list, active_session=active_session)

    if fee_status == "has_dues":
        students_list = [s for s in students_list if s.has_dues]
    elif fee_status == "cleared":
        students_list = [s for s in students_list if not s.has_dues]

    headers = [
        "Admission #",
        "Full Name",
        "Father Name",
        "Gender",
        "Date of Birth",
        "Class",
        "Section",
        "Family ID",
        "Contact Number",
        "Residence Address",
        "Status",
        "Fee Status",
        "Total Dues (PKR)",
        "Paid Months",
        "Pending Months & Dues",
        "Family Total Dues (PKR)",
        "Admission Date",
    ]

    rows = []
    for s in students_list:
        rows.append([
            s.admission_no,
            s.full_name,
            s.father_name,
            s.gender,
            s.dob.strftime("%Y-%m-%d") if s.dob else "",
            s.current_class.name if s.current_class else "",
            s.current_section.name if s.current_section else "",
            s.family.family_id if s.family else "",
            s.contact_number,
            s.residence,
            s.status,
            "Outstanding Dues" if s.has_dues else "Cleared",
            float(s.total_dues),
            ", ".join(s.paid_months_list) if s.paid_months_list else "None",
            s.pending_months_display,
            float(s.family_total_dues) if s.family else 0.0,
            s.admission_date.strftime("%Y-%m-%d") if s.admission_date else "",
        ])

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    buffer = create_styled_workbook("Student Directory", headers, rows)
    return excel_download_response(buffer, f"KMS_Students_Export_{timestamp}.xlsx")


@login_required
def download_student_template(request):
    """
    Download empty/sample Excel template for bulk student onboarding.
    """
    from school.excel_utils import create_styled_workbook, excel_download_response

    headers = [
        "Admission # (Optional)",
        "Full Name *",
        "Father Name *",
        "Gender (Male/Female) *",
        "Date of Birth (YYYY-MM-DD)",
        "Class Name *",
        "Section (A/B/C)",
        "Contact Number",
        "Residence Address",
        "Status (Active/Withdrawn)",
        "Admission Date (YYYY-MM-DD)",
    ]

    sample_rows = [
        [
            "1051",
            "Muhammad Hamza",
            "Tariq Mahmood",
            "Male",
            "2015-04-12",
            "Class 5",
            "A",
            "0345-9876543",
            "Qalagay, Swat",
            "Active",
            "2026-03-01",
        ],
        [
            "1052",
            "Fatima Noor",
            "Abdul Rashid",
            "Female",
            "2016-08-25",
            "Class 4",
            "B",
            "0300-1234567",
            "Barikot, Swat",
            "Active",
            "2026-03-01",
        ],
    ]

    buffer = create_styled_workbook("Students Import Template", headers, sample_rows)
    return excel_download_response(buffer, "KMS_Students_Sample_Template.xlsx")


@login_required
def import_students_excel(request):
    """
    Bulk import students from Excel file with automated class, section,
    family matching, and 12-month fee ledger initialization.
    """
    from datetime import datetime, date
    from school.excel_utils import parse_excel_upload

    if request.method != "POST" or "excel_file" not in request.FILES:
        messages.error(request, "Please select an Excel file (.xlsx) to upload.")
        return redirect("student_list")

    excel_file = request.FILES["excel_file"]
    records, errors = parse_excel_upload(excel_file, header_row=2)

    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect("student_list")

    if not records:
        messages.warning(request, "The uploaded Excel file contains no student data rows.")
        return redirect("student_list")

    active_session = AcademicSession.objects.filter(is_active=True).first()
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

    with transaction.atomic():
        for r in records:
            row_num = r.get("_row_number", "?")
            full_name = str(r.get("full_name__", "") or r.get("full_name", "")).strip()
            father_name = str(r.get("father_name__", "") or r.get("father_name", "")).strip()

            if not full_name:
                row_errors.append(f"Row {row_num}: Missing Full Name.")
                continue

            # Class matching or auto-creation
            class_raw = str(r.get("class_name__", "") or r.get("class", "") or r.get("class_name", "")).strip()
            class_obj = None
            if class_raw:
                class_obj = ClassLevel.objects.filter(name__iexact=class_raw).first()
                if not class_obj:
                    class_obj = ClassLevel.objects.create(name=class_raw, level="Primary", monthly_fee=Decimal("1500.00"))

            # Section matching or default
            section_raw = str(r.get("section__a_b_c_", "") or r.get("section", "A")).strip().upper() or "A"
            section_obj = None
            if class_obj:
                section_obj = Section.objects.filter(class_level=class_obj, name__iexact=section_raw).first()
                if not section_obj:
                    section_obj = Section.objects.create(class_level=class_obj, name=section_raw)

            # Gender
            gender_raw = str(r.get("gender__male_female___", "") or r.get("gender", "Male")).strip().capitalize()
            gender = gender_raw if gender_raw in ["Male", "Female"] else "Male"

            # Contact & Address
            contact = str(r.get("contact_number", "") or "").strip()
            residence = str(r.get("residence_address", "") or r.get("residence", "")).strip()

            # Family matching or creation
            family = None
            if father_name:
                family = FamilyHousehold.objects.filter(father_guardian_name__iexact=father_name).first()
                if not family and contact:
                    family = FamilyHousehold.objects.filter(contact_number=contact).first()
                if not family:
                    family = FamilyHousehold.objects.create(
                        father_guardian_name=father_name,
                        contact_number=contact,
                        address=residence,
                    )

            # Dates
            dob = parse_date(r.get("date_of_birth__yyyy_mm_dd_", None) or r.get("date_of_birth", None))
            adm_date = parse_date(r.get("admission_date__yyyy_mm_dd_", None) or r.get("admission_date", None)) or timezone.now().date()

            # Status
            status_raw = str(r.get("status__active_withdrawn_", "") or r.get("status", "Active")).strip().capitalize()
            status = "Withdrawn" if "withdrawn" in status_raw.lower() else "Active"

            # Admission number
            adm_no = str(r.get("admission_no__optional_", "") or r.get("admission_no", "") or r.get("admission_no", "")).strip()
            if adm_no and Student.objects.filter(admission_no=adm_no).exists():
                adm_no = ""  # Force auto-generation if duplicate exists

            student = Student(
                full_name=full_name,
                father_name=father_name,
                gender=gender,
                dob=dob or date(2015, 1, 1),
                current_class=class_obj,
                current_section=section_obj,
                family=family,
                contact_number=contact,
                residence=residence,
                status=status,
                admission_date=adm_date,
            )
            if adm_no:
                student.admission_no = adm_no
            student.save()

            # Initialize 12-month Fee Ledger if active session exists
            if active_session and class_obj:
                ledger, _ = StudentFeeLedger.objects.get_or_create(
                    student=student,
                    academic_session=active_session,
                )
                initialize_ledger_months(ledger, student, class_obj.monthly_fee)

            success_count += 1

    if success_count > 0:
        messages.success(request, f"Excel Import Completed! Successfully imported {success_count} student records with automated 12-month fee ledgers.")
    if row_errors:
        messages.warning(request, f"Some rows were skipped: {'; '.join(row_errors[:5])}")

    return redirect("student_list")

