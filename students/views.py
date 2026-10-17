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

from finance.models import StudentFeeLedger
from finance.utils import apply_withdrawal_stop, initialize_ledger_months, roll_over_arrears
from school.models import AcademicSession, ClassLevel, Section, SchoolSetting
from school.whatsapp_utils import build_student_dues_reminder_msg
from .forms import FamilyHouseholdForm, SinglePromoteForm, StudentForm, StudentWithdrawForm
from .models import FamilyHousehold, PromotionHistory, Student, StudentAttendance


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
    Searchable, filterable student directory with:
    - Demographic data (Name, Father, Address, Age, Class, Section, Gender)
    - School-wide male & female counts and percentages
    - Class-wise and Section-wise counts, male/female absents with percentage-wise breakdown
    - Fee ledger status & balance
    """
    students_qs = Student.objects.select_related(
        "current_class", "current_section", "family"
    ).all()

    query = request.GET.get("q", "").strip()
    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")
    gender = request.GET.get("gender", "")
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
    if gender:
        students_qs = students_qs.filter(gender=gender)
    if status:
        students_qs = students_qs.filter(status=status)

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    students_list = list(students_qs)
    compute_students_fee_ledger_map(students_list, active_session=active_session)

    # 1. School-wide Global Demographics (across ALL active students)
    active_all_students = Student.objects.filter(status="Active")
    total_active_school = active_all_students.count()
    school_male_count = active_all_students.filter(gender="Male").count()
    school_female_count = active_all_students.filter(gender="Female").count()
    school_male_pct = round((school_male_count / total_active_school * 100), 1) if total_active_school > 0 else 0.0
    school_female_pct = round((school_female_count / total_active_school * 100), 1) if total_active_school > 0 else 0.0

    # 2. Today's Daily Attendance & Absent Counts & Percentages
    today_date = timezone.now().date()
    today_att_qs = StudentAttendance.objects.filter(date=today_date, student__status="Active")
    today_present_count = today_att_qs.filter(status__in=["Present", "Late"]).count()
    today_absent_count = today_att_qs.filter(status="Absent").count()

    today_male_present = today_att_qs.filter(student__gender="Male", status__in=["Present", "Late"]).count()
    today_male_absent = today_att_qs.filter(student__gender="Male", status="Absent").count()
    today_male_absent_pct = round((today_male_absent / school_male_count * 100), 1) if school_male_count > 0 else 0.0

    today_female_present = today_att_qs.filter(student__gender="Female", status__in=["Present", "Late"]).count()
    today_female_absent = today_att_qs.filter(student__gender="Female", status="Absent").count()
    today_female_absent_pct = round((today_female_absent / school_female_count * 100), 1) if school_female_count > 0 else 0.0

    today_tot_marked = today_present_count + today_absent_count
    today_overall_att_pct = round((today_present_count / today_tot_marked * 100), 1) if today_tot_marked > 0 else 0.0

    # 3. Class-wise and Section-wise Detailed Breakdown Matrix
    class_breakdown = []
    classes_all = ClassLevel.objects.prefetch_related("sections").all()
    for cl in classes_all:
        for sec in cl.sections.all():
            sec_students = active_all_students.filter(current_class=cl, current_section=sec)
            sec_tot = sec_students.count()
            if sec_tot == 0:
                continue
            sec_m = sec_students.filter(gender="Male").count()
            sec_f = sec_students.filter(gender="Female").count()

            # Today attendances for this class/section
            sec_att = today_att_qs.filter(student__current_class=cl, student__current_section=sec)
            sec_m_p = sec_att.filter(student__gender="Male", status__in=["Present", "Late"]).count()
            sec_m_a = sec_att.filter(student__gender="Male", status="Absent").count()
            sec_m_a_pct = round((sec_m_a / sec_m * 100), 1) if sec_m > 0 else 0.0

            sec_f_p = sec_att.filter(student__gender="Female", status__in=["Present", "Late"]).count()
            sec_f_a = sec_att.filter(student__gender="Female", status="Absent").count()
            sec_f_a_pct = round((sec_f_a / sec_f * 100), 1) if sec_f > 0 else 0.0

            sec_tot_p = sec_m_p + sec_f_p
            sec_tot_a = sec_m_a + sec_f_a
            sec_att_pct = round((sec_tot_p / (sec_tot_p + sec_tot_a) * 100), 1) if (sec_tot_p + sec_tot_a) > 0 else 0.0

            class_breakdown.append({
                "class_level": cl,
                "section": sec,
                "total_enrolled": sec_tot,
                "male_count": sec_m,
                "female_count": sec_f,
                "male_present": sec_m_p,
                "male_absent": sec_m_a,
                "male_absent_pct": sec_m_a_pct,
                "female_present": sec_f_p,
                "female_absent": sec_f_a,
                "female_absent_pct": sec_f_a_pct,
                "attendance_pct": sec_att_pct,
            })

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
    selected_class_obj = ClassLevel.objects.filter(id=class_id).first() if class_id else None

    context = {
        "students": students_list,
        "classes": classes,
        "sections": sections,
        "query": query,
        "selected_class": class_id,
        "selected_class_obj": selected_class_obj,
        "selected_section": section_id,
        "selected_gender": gender,
        "selected_status": status,
        "selected_fee_status": fee_status,
        "active_session": active_session,
        "total_active_students": total_active_students,
        "total_students_with_dues": total_students_with_dues,
        "total_cleared_students": total_cleared_students,
        "total_outstanding_school_dues": total_outstanding_school_dues,
        # School-Wide Gender Counts & Pct
        "total_active_school": total_active_school,
        "school_male_count": school_male_count,
        "school_female_count": school_female_count,
        "school_male_pct": school_male_pct,
        "school_female_pct": school_female_pct,
        # Today's Absents & Attendance
        "today_date": today_date,
        "today_male_present": today_male_present,
        "today_male_absent": today_male_absent,
        "today_male_absent_pct": today_male_absent_pct,
        "today_female_present": today_female_present,
        "today_female_absent": today_female_absent,
        "today_female_absent_pct": today_female_absent_pct,
        "today_overall_att_pct": today_overall_att_pct,
        # Class-Wise Breakdown
        "class_breakdown": class_breakdown,
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
                active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
                if not active_session:
                    active_session = AcademicSession.objects.create(name="2026-2027", is_active=True)
                if active_session:
                    ledger, created = StudentFeeLedger.objects.get_or_create(
                        student=student, academic_session=active_session
                    )
                    if created or ledger.monthly_entries.count() < 12:
                        initialize_ledger_months(
                            ledger,
                            student,
                            student.effective_monthly_fee,
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

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    if not active_session:
        active_session = AcademicSession.objects.create(name="2026-2027", is_active=True)

    active_ledger = None
    if active_session:
        active_ledger, created = StudentFeeLedger.objects.get_or_create(
            student=student, academic_session=active_session
        )
        if created or active_ledger.monthly_entries.count() < 12:
            initialize_ledger_months(
                active_ledger,
                student,
                student.effective_monthly_fee,
                admission_date=student.admission_date,
            )

    ledgers = student.fee_ledgers.select_related("academic_session").prefetch_related(
        "monthly_entries"
    ).all()

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

                # Sync customized/free fee to unpaid entries in active session ledger
                active_sess = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
                if active_sess:
                    st_ledger = StudentFeeLedger.objects.filter(student=updated_student, academic_session=active_sess).first()
                    if st_ledger:
                        new_fee = updated_student.effective_monthly_fee
                        unpaid_entries = st_ledger.monthly_entries.filter(paid_amount=Decimal("0.00"))
                        if unpaid_entries.exists():
                            unpaid_entries.update(monthly_fee=new_fee)
                            recalculate_ledger_arrears(st_ledger)

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


def date_to_words(d):
    """
    Converts a date object or string into formal official words for certificates.
    Example: 2012-05-14 -> 'Fourteenth May Two Thousand Twelve'
    """
    if not d:
        return ""
    if isinstance(d, str):
        try:
            from datetime import datetime
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            return d

    days = {
        1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
        6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth",
        11: "Eleventh", 12: "Twelfth", 13: "Thirteenth", 14: "Fourteenth",
        15: "Fifteenth", 16: "Sixteenth", 17: "Seventeenth", 18: "Eighteenth",
        19: "Nineteenth", 20: "Twentieth", 21: "Twenty-First", 22: "Twenty-Second",
        23: "Twenty-Third", 24: "Twenty-Fourth", 25: "Twenty-Fifth",
        26: "Twenty-Sixth", 27: "Twenty-Seventh", 28: "Twenty-Eighth",
        29: "Twenty-Ninth", 30: "Thirtieth", 31: "Thirty-First"
    }
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    def num_to_words(n):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            rem = n % 10
            return tens[n // 10] + ("-" + units[rem] if rem else "")
        elif n < 1000:
            rem = n % 100
            return units[n // 100] + " Hundred" + (" and " + num_to_words(rem) if rem else "")
        elif n < 10000:
            rem = n % 1000
            th = n // 1000
            if rem == 0:
                return num_to_words(th) + " Thousand"
            elif rem < 100:
                return num_to_words(th) + " Thousand " + num_to_words(rem)
            else:
                return num_to_words(th) + " Thousand " + num_to_words(rem)
        return str(n)

    day_str = days.get(d.day, str(d.day))
    month_str = months.get(d.month, str(d.month))
    year_str = num_to_words(d.year)
    return f"{day_str} {month_str} {year_str}"


@login_required
def dob_certificate(request, pk=None):
    """
    Printable Official Date of Birth (D.O.B) Certificate (School Based).
    Matches official AWR format with DOB in figures and words.
    Supports viewing for a specific student or printing blank.
    """
    from school.models import SchoolSetting, AcademicSession
    student = None
    student_id = pk or request.GET.get("student_id")
    if student_id:
        student = get_object_or_404(Student, pk=student_id)

    school_setting = SchoolSetting.objects.first()
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    all_students = Student.objects.filter(status="Active").select_related("current_class", "current_section").order_by("current_class__name", "admission_no")

    dob_in_words = ""
    dob_in_figures = ""
    if student and student.dob:
        dob_in_figures = student.dob.strftime("%d-%m-%Y")
        dob_in_words = date_to_words(student.dob)

    is_blank = request.GET.get("blank") == "1"
    if is_blank:
        student = None
        dob_in_figures = ""
        dob_in_words = ""

    return render(
        request,
        "students/dob_certificate.html",
        {
            "student": student,
            "dob_in_figures": dob_in_figures,
            "dob_in_words": dob_in_words,
            "school_setting": school_setting,
            "active_session": active_session,
            "all_students": all_students,
            "is_blank": is_blank,
        },
    )


@login_required
def blank_admission_form(request):
    """
    Official blank printable Student Admission & Registration Form (PDF/Print)
    for parents who need a physical form to take home and fill in child details.
    """
    from school.models import SchoolSetting, ClassLevel, AcademicSession
    school_setting = SchoolSetting.objects.first()
    class_levels = ClassLevel.objects.all().order_by("name")
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    selected_class_id = request.GET.get("class_id")
    selected_class = None
    if selected_class_id:
        selected_class = ClassLevel.objects.filter(id=selected_class_id).first()

    return render(
        request,
        "students/blank_admission_form.html",
        {
            "school_setting": school_setting,
            "class_levels": class_levels,
            "selected_class": selected_class,
            "active_session": active_session,
        },
    )


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
    from school.excel_utils import clean_adm_no, parse_excel_upload, resolve_class_level

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
    created_count = 0
    updated_count = 0
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

    try:
        with transaction.atomic():
            for r in records:
                row_num = r.get("_row_number", "?")
                full_name = str(r.get("full_name") or r.get("full_name__") or r.get("name", "")).strip()
                father_name = str(r.get("father_name") or r.get("father_name__") or r.get("father", "")).strip()

                if not full_name:
                    row_errors.append(f"Row {row_num}: Missing Full Name.")
                    continue

                # Class matching via intelligent resolver or fallback auto-creation
                class_raw = str(r.get("class_name") or r.get("class_name__") or r.get("class") or r.get("grade", "")).strip()
                class_obj = resolve_class_level(class_raw) if class_raw else None
                if not class_obj and class_raw:
                    class_obj = ClassLevel.objects.create(name=class_raw, level="Primary", monthly_fee=Decimal("1500.00"))

                # Section matching or default
                section_raw = str(r.get("section") or r.get("section_a_b_c") or r.get("section__a_b_c_", "A")).strip().upper() or "A"
                section_obj = None
                if class_obj:
                    section_obj = Section.objects.filter(class_level=class_obj, name__iexact=section_raw).first()
                    if not section_obj:
                        section_obj = Section.objects.create(class_level=class_obj, name=section_raw)

                # Gender
                gender_raw = str(r.get("gender") or r.get("gender_male_female") or r.get("gender__male_female___", "Male")).strip().capitalize()
                gender = gender_raw if gender_raw in ["Male", "Female"] else "Male"

                # Contact & Address
                contact = str(r.get("contact_number") or r.get("contact") or r.get("phone", "")).strip()
                residence = str(r.get("residence_address") or r.get("residence") or r.get("address", "")).strip()

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
                dob = parse_date(r.get("dob") or r.get("date_of_birth") or r.get("date_of_birth_yyyy_mm_dd") or r.get("date_of_birth__yyyy_mm_dd_"))
                adm_date = parse_date(r.get("admission_date") or r.get("admission_date_yyyy_mm_dd") or r.get("admission_date__yyyy_mm_dd_")) or timezone.now().date()

                # Status
                status_raw = str(r.get("status") or r.get("status_active_withdrawn") or r.get("status__active_withdrawn_", "Active")).strip().capitalize()
                status = "Withdrawn" if "withdrawn" in status_raw.lower() else "Active"

                # Check for existing student by admission number or name+father+class (Prevent Duplicates)
                adm_no = clean_adm_no(
                    r.get("admission_no") or r.get("admission_optional") or r.get("admission_no__optional_") or
                    r.get("admission") or r.get("roll_no") or r.get("roll") or r.get("reg_no") or ""
                )
                student = None
                if adm_no and class_obj:
                    # Match strictly within designated class
                    student = Student.objects.filter(current_class=class_obj, admission_no__iexact=adm_no).first()
                elif adm_no and not class_obj:
                    student = Student.objects.filter(admission_no__iexact=adm_no).first()

                if not student and full_name and father_name and class_obj:
                    # Only match by name if the candidate has matching father name and no conflicting admission_no
                    candidate = Student.objects.filter(
                        full_name__iexact=full_name,
                        father_name__iexact=father_name,
                        current_class=class_obj,
                    ).first()
                    if candidate and (not candidate.admission_no or not adm_no or clean_adm_no(candidate.admission_no).lower() == adm_no.lower()):
                        student = candidate

                if student:
                    # Update existing student - DO NOT DUPLICATE
                    student.full_name = full_name
                    student.father_name = father_name
                    student.gender = gender
                    if adm_no and not student.admission_no:
                        student.admission_no = adm_no
                    if dob:
                        student.dob = dob
                    if class_obj:
                        student.current_class = class_obj
                    if section_obj:
                        student.current_section = section_obj
                    if family:
                        student.family = family
                    if contact:
                        student.contact_number = contact
                    if residence:
                        student.residence = residence
                    student.status = status
                    student.save()
                    updated_count += 1
                else:
                    # Create new student
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
                        admission_no=adm_no,  # Set directly! No cross-class rejection!
                    )
                    student.save()
                    created_count += 1

                # Initialize 12-month Fee Ledger if active session exists
                if active_session and class_obj:
                    ledger, _ = StudentFeeLedger.objects.get_or_create(
                        student=student,
                        academic_session=active_session,
                    )
                    initialize_ledger_months(ledger, student, class_obj.monthly_fee)

        total_processed = created_count + updated_count
        if total_processed > 0:
            messages.success(
                request,
                f"Excel Import Completed! Created {created_count} new student(s), updated {updated_count} existing record(s) with no duplicates."
            )
        if row_errors:
            messages.warning(request, f"Some rows had warnings: {'; '.join(row_errors[:5])}")
    except Exception as e:
        messages.error(request, f"Excel Import Failed: {str(e)}")

    return redirect("student_list")


@login_required
def student_delete(request, pk):
    """
    Deletes an individual student record and all associated records cleanly.
    """
    student = get_object_or_404(Student, pk=pk)
    name = student.full_name
    adm = student.admission_no
    class_name = student.current_class.name if student.current_class else ""
    next_url = request.POST.get("next") or request.GET.get("next") or request.META.get("HTTP_REFERER") or "/students/"

    if request.method == "POST":
        try:
            with transaction.atomic():
                student.delete()
            messages.success(request, f"Student '{name}' (Adm #{adm}, {class_name}) was successfully deleted.")
        except Exception as e:
            messages.error(request, f"Error deleting student '{name}': {str(e)}")
        return redirect(next_url)

    return render(request, "students/student_confirm_delete.html", {
        "student": student,
        "next": next_url,
    })


@login_required
def student_bulk_delete(request):
    """
    Bulk deletes selected students by their primary keys.
    """
    if request.method != "POST":
        return redirect("student_list")

    student_ids = request.POST.getlist("student_ids")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/students/"

    if not student_ids:
        messages.warning(request, "No students were selected for deletion.")
        return redirect(next_url)

    try:
        with transaction.atomic():
            qs = Student.objects.filter(id__in=student_ids)
            count = qs.count()
            qs.delete()
        messages.success(request, f"Successfully deleted {count} selected student(s).")
    except Exception as e:
        messages.error(request, f"Error deleting selected students: {str(e)}")

    return redirect(next_url)


@login_required
def class_students_delete(request, class_id):
    """
    Deletes all students enrolled in a specified class (useful for wrong Excel imports or resets).
    """
    if request.method != "POST":
        return redirect("student_list")

    class_level = get_object_or_404(ClassLevel, id=class_id)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or f"/students/?current_class={class_id}"

    try:
        with transaction.atomic():
            qs = Student.objects.filter(current_class=class_level)
            count = qs.count()
            qs.delete()
        messages.success(request, f"Successfully deleted all {count} student(s) from {class_level.name}.")
    except Exception as e:
        messages.error(request, f"Error deleting students of {class_level.name}: {str(e)}")

    return redirect(next_url)


# ==============================================================================
# STUDENT QR CODE & ID CARDS SYSTEM (KMS V4)
# ==============================================================================

@login_required
def student_qr_image(request, pk):
    """
    Streams dynamic PNG QR code for a student.
    """
    student = get_object_or_404(Student, pk=pk)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(str(student.admission_no or student.id))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@login_required
def student_id_card(request, pk):
    """
    Printable individual student ID Card with scannable QR Code.
    """
    student = get_object_or_404(
        Student.objects.select_related("current_class", "current_section", "family"),
        pk=pk,
    )
    school_setting = SchoolSetting.objects.first()
    return render(
        request,
        "students/student_id_card.html",
        {
            "student": student,
            "school_setting": school_setting,
        },
    )


@login_required
def all_student_id_cards(request):
    """
    Bulk printable Student ID Cards with scannable QR Codes, filterable by Class and Section.
    """
    students_qs = Student.objects.filter(status="Active").select_related(
        "current_class", "current_section", "family"
    ).order_by("current_class__id", "current_section__name", "admission_no")

    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")

    if class_id:
        students_qs = students_qs.filter(current_class_id=class_id)
    if section_id:
        students_qs = students_qs.filter(current_section_id=section_id)

    classes = ClassLevel.objects.all()
    sections = Section.objects.all()
    school_setting = SchoolSetting.objects.first()

    return render(
        request,
        "students/all_student_id_cards.html",
        {
            "students": students_qs,
            "classes": classes,
            "sections": sections,
            "selected_class": class_id,
            "selected_section": section_id,
            "school_setting": school_setting,
        },
    )


# ==============================================================================
# STUDENT QUICK QR ATTENDANCE SCANNER
# ==============================================================================

@login_required
def student_qr_attendance_scan(request):
    """
    Live real-time webcam and USB barcode/QR scanner terminal for student attendance.
    Includes Morning IN and Afternoon OUT modes, live stats, and custom updates.
    """
    today = timezone.localtime(timezone.now()).date()
    today_attendances = (
        StudentAttendance.objects.filter(date=today)
        .select_related("student", "student__current_class", "student__current_section")
        .order_by("-updated_at")
    )

    total_scanned = today_attendances.count()
    male_scanned = today_attendances.filter(student__gender="Male").count()
    female_scanned = today_attendances.filter(student__gender="Female").count()
    total_out = today_attendances.filter(check_out__isnull=False).count()
    still_in_count = today_attendances.filter(check_in__isnull=False, check_out__isnull=True).count()

    active_students = Student.objects.filter(status="Active").select_related("current_class", "current_section").order_by("admission_no")

    return render(
        request,
        "students/student_qr_scan.html",
        {
            "today": today,
            "today_attendances": today_attendances[:150],
            "total_scanned": total_scanned,
            "male_scanned": male_scanned,
            "female_scanned": female_scanned,
            "total_out": total_out,
            "still_in_count": still_in_count,
            "active_students": active_students,
        },
    )


@login_required
def api_process_student_qr_scan(request):
    """
    Fast JSON API to mark student attendance instantly from QR scan or barcode.
    Supports scan_mode: 'auto', 'in', or 'out'.
    """
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    code = ""
    scan_mode = "auto"
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8")) if request.body else {}
            code = data.get("code", "")
            scan_mode = data.get("scan_mode", "auto")
        except Exception:
            code = request.POST.get("code", "")
            scan_mode = request.POST.get("scan_mode", "auto")
    if not code:
        code = request.GET.get("code", "")
        scan_mode = request.GET.get("scan_mode", "auto")

    code = str(code).strip()
    if not code:
        return JsonResponse({"status": "error", "message": "No QR Code received."}, status=400)

    # Clean prefix if any
    clean_code = code
    if "KMS-STUDENT:" in code.upper():
        clean_code = code.split(":", 1)[1].strip()
    elif " - " in clean_code:
        clean_code = clean_code.split(" - ")[0].strip()

    # Resolve student by admission_no or ID or Name
    student = Student.objects.filter(
        Q(admission_no__iexact=clean_code) |
        Q(admission_no__iexact=code)
    ).select_related("current_class", "current_section").first()

    if not student and clean_code.isdigit():
        student = Student.objects.filter(id=int(clean_code)).select_related("current_class", "current_section").first()

    if not student:
        student = Student.objects.filter(full_name__iexact=clean_code).select_related("current_class", "current_section").first()

    if not student:
        return JsonResponse({
            "status": "error",
            "message": f"Student with Admission No '{code}' not found in registry.",
        }, status=404)

    today = timezone.localtime(timezone.now()).date()
    now_time = timezone.localtime(timezone.now()).time().replace(microsecond=0)

    att = StudentAttendance.objects.filter(student=student, date=today).first()
    action = "in"
    already_marked = False

    if not att:
        # First entry of the day
        if scan_mode == "out":
            att = StudentAttendance.objects.create(
                student=student,
                date=today,
                status="Present",
                check_in=now_time,
                check_out=now_time,
                attendance_method="QR Code",
                remarks="Checked Out via QR Scan",
            )
            action = "out"
            msg = f"SUCCESS: {student.full_name} marked Out ({now_time.strftime('%I:%M %p')})."
        else:
            att = StudentAttendance.objects.create(
                student=student,
                date=today,
                status="Present",
                check_in=now_time,
                attendance_method="QR Code",
                remarks="Morning Check-In via QR Scan",
            )
            action = "in"
            msg = f"SUCCESS: {student.full_name} marked Present / Check-In ({now_time.strftime('%I:%M %p')})."
    else:
        # Existing record
        if scan_mode == "out":
            att.check_out = now_time
            att.attendance_method = "QR Code"
            att.save()
            action = "out"
            msg = f"SUCCESS: {student.full_name} Departure / Check-Out recorded ({now_time.strftime('%I:%M %p')})."
        elif scan_mode == "in":
            already_marked = True
            in_str = att.check_in.strftime('%I:%M %p') if att.check_in else 'Earlier'
            msg = f"{student.full_name} was already checked in at {in_str}."
        else:
            # Auto mode: if has check_in but no check_out, record check_out
            if not att.check_out:
                att.check_out = now_time
                att.save()
                action = "out"
                msg = f"SUCCESS: {student.full_name} Departure / Check-Out recorded ({now_time.strftime('%I:%M %p')})."
            else:
                att.check_out = now_time
                att.save()
                action = "out"
                msg = f"Check-Out updated for {student.full_name} at {now_time.strftime('%I:%M %p')}."

    # Summary counts for today
    today_all = StudentAttendance.objects.filter(date=today)
    tot_count = today_all.count()
    m_count = today_all.filter(student__gender="Male").count()
    f_count = today_all.filter(student__gender="Female").count()
    out_count = today_all.filter(check_out__isnull=False).count()
    still_count = today_all.filter(check_in__isnull=False, check_out__isnull=True).count()

    photo_url = student.profile_picture.url if student.profile_picture else ""

    return JsonResponse({
        "status": "warning" if already_marked else "success",
        "action": action,
        "already_marked": already_marked,
        "message": msg,
        "student": {
            "id": student.id,
            "admission_no": student.admission_no,
            "name": student.full_name,
            "father_name": student.father_name,
            "gender": student.gender,
            "class_name": student.current_class.name if student.current_class else "---",
            "section_name": student.current_section.name if student.current_section else "---",
            "photo_url": photo_url,
            "status": att.status,
            "check_in": att.check_in.strftime("%I:%M %p") if att.check_in else "---",
            "check_out": att.check_out.strftime("%I:%M %p") if att.check_out else "---",
            "attendance_method": att.attendance_method,
        },
        "stats": {
            "total_scanned": tot_count,
            "male_scanned": m_count,
            "female_scanned": f_count,
            "total_out": out_count,
            "still_in": still_count,
        }
    })


@login_required
def api_update_student_attendance(request):
    """
    Custom override API for Principal & Vice Principal to modify attendance status,
    check_in, check_out, or remarks for any student on a given date.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else request.POST
    except Exception:
        data = request.POST

    student_id = data.get("student_id")
    date_str = data.get("date")
    new_status = data.get("status", "Present")
    check_in_str = data.get("check_in", "").strip()
    check_out_str = data.get("check_out", "").strip()
    remarks = data.get("remarks", "").strip()

    student = get_object_or_404(Student, pk=student_id)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.localtime(timezone.now()).date()
    else:
        target_date = timezone.localtime(timezone.now()).date()

    check_in_val = None
    if check_in_str:
        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M%p"):
            try:
                check_in_val = datetime.strptime(check_in_str, fmt).time()
                break
            except ValueError:
                pass

    check_out_val = None
    if check_out_str:
        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M%p"):
            try:
                check_out_val = datetime.strptime(check_out_str, fmt).time()
                break
            except ValueError:
                pass

    att, _ = StudentAttendance.objects.get_or_create(
        student=student,
        date=target_date,
        defaults={"attendance_method": "Manual"}
    )
    att.status = new_status
    if check_in_val or check_in_str:
        att.check_in = check_in_val
    if check_out_val or check_out_str:
        att.check_out = check_out_val
    att.remarks = remarks or f"Modified by Principal/VP ({request.user.username})"
    att.attendance_method = "Manual Override"
    att.save()

    # Recalculate stats
    today_all = StudentAttendance.objects.filter(date=target_date)
    photo_url = student.profile_picture.url if student.profile_picture else ""
    return JsonResponse({
        "status": "success",
        "message": f"Updated attendance for {student.full_name} ({att.status}).",
        "student": {
            "id": student.id,
            "admission_no": student.admission_no,
            "name": student.full_name,
            "father_name": student.father_name,
            "gender": student.gender,
            "class_name": student.current_class.name if student.current_class else "---",
            "section_name": student.current_section.name if student.current_section else "---",
            "photo_url": photo_url,
            "status": att.status,
            "check_in": att.check_in.strftime("%I:%M %p") if att.check_in else "---",
            "check_out": att.check_out.strftime("%I:%M %p") if att.check_out else "---",
            "attendance_method": att.attendance_method,
            "remarks": att.remarks,
        },
        "stats": {
            "total_scanned": today_all.count(),
            "male_scanned": today_all.filter(student__gender="Male").count(),
            "female_scanned": today_all.filter(student__gender="Female").count(),
            "total_out": today_all.filter(check_out__isnull=False).count(),
            "still_in": today_all.filter(check_in__isnull=False, check_out__isnull=True).count(),
        }
    })


# ==============================================================================
# CLASS-WISE DAILY ATTENDANCE REGISTER
# ==============================================================================

@login_required
def student_daily_attendance(request):
    """
    Class-wise daily attendance register with:
    - S#, Adm#, Name, Father, Gender, Status radio buttons
    - One-click Mark All Present
    - School & Class level gender stats (Male/Female present & absent with percentages!)
    """
    classes = ClassLevel.objects.prefetch_related("sections").all()
    selected_class_id = request.GET.get("class_id") or (str(classes.first().id) if classes.exists() else "")
    selected_class = ClassLevel.objects.filter(id=selected_class_id).first() if selected_class_id else None

    sections = selected_class.sections.all() if selected_class else Section.objects.none()
    selected_section_id = request.GET.get("section_id") or (str(sections.first().id) if sections.exists() else "")
    selected_section = Section.objects.filter(id=selected_section_id).first() if selected_section_id else None

    date_str = request.GET.get("date", "")
    if date_str:
        try:
            att_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            att_date = timezone.localtime(timezone.now()).date()
    else:
        att_date = timezone.localtime(timezone.now()).date()

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    # Process Form POST (Save Register)
    if request.method == "POST":
        with transaction.atomic():
            saved_count = 0
            for s in students:
                field_name = f"status_{s.id}"
                new_status = request.POST.get(field_name, "Present")
                if new_status in ["Present", "Late", "Absent", "Leave", "Holiday"]:
                    obj, created = StudentAttendance.objects.get_or_create(
                        student=s,
                        date=att_date,
                        defaults={
                            "status": new_status,
                            "attendance_method": "Manual",
                            "check_in": timezone.localtime(timezone.now()).time() if new_status in ["Present", "Late"] else None,
                        }
                    )
                    if not created:
                        obj.status = new_status
                        obj.save()
                    saved_count += 1
            messages.success(request, f"Attendance saved successfully for {saved_count} student(s) on {att_date.strftime('%d-%b-%Y')}.")
            return redirect(f"{reverse('student_daily_attendance')}?class_id={selected_class_id}&section_id={selected_section_id}&date={att_date.strftime('%Y-%m-%d')}")

    # Fetch existing attendance records for this date
    att_map = {}
    if students:
        records = StudentAttendance.objects.filter(student__in=students, date=att_date)
        att_map = {r.student_id: r for r in records}

    # Attach attendance object to each student for template
    for s in students:
        s.daily_record = att_map.get(s.id)
        s.current_status = s.daily_record.status if s.daily_record else "Present"

    # Class Demographic & Today's Attendance Metrics
    total_enrolled = len(students)
    male_enrolled = len([s for s in students if s.gender == "Male"])
    female_enrolled = len([s for s in students if s.gender == "Female"])

    present_count = len([s for s in students if s.current_status in ["Present", "Late"]])
    absent_count = len([s for s in students if s.current_status == "Absent"])
    leave_count = len([s for s in students if s.current_status == "Leave"])

    male_present = len([s for s in students if s.gender == "Male" and s.current_status in ["Present", "Late"]])
    male_absent = len([s for s in students if s.gender == "Male" and s.current_status == "Absent"])
    male_absent_pct = round((male_absent / male_enrolled * 100), 1) if male_enrolled > 0 else 0.0

    female_present = len([s for s in students if s.gender == "Female" and s.current_status in ["Present", "Late"]])
    female_absent = len([s for s in students if s.gender == "Female" and s.current_status == "Absent"])
    female_absent_pct = round((female_absent / female_enrolled * 100), 1) if female_enrolled > 0 else 0.0

    tot_evaluated = present_count + absent_count
    attendance_pct = round((present_count / tot_evaluated * 100), 1) if tot_evaluated > 0 else 0.0

    return render(
        request,
        "students/student_daily_attendance.html",
        {
            "classes": classes,
            "sections": sections,
            "selected_class": selected_class,
            "selected_section": selected_section,
            "selected_class_id": selected_class_id,
            "selected_section_id": selected_section_id,
            "att_date": att_date,
            "students": students,
            "total_enrolled": total_enrolled,
            "male_enrolled": male_enrolled,
            "female_enrolled": female_enrolled,
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "male_present": male_present,
            "male_absent": male_absent,
            "male_absent_pct": male_absent_pct,
            "female_present": female_present,
            "female_absent": female_absent,
            "female_absent_pct": female_absent_pct,
            "attendance_pct": attendance_pct,
        },
    )


@login_required
def student_daily_attendance_print(request):
    """
    Official printable Class Attendance Register Sheet (matching KOHISAR MODEL SCHOOL register format).
    """
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    date_str = request.GET.get("date", "")
    school_setting = SchoolSetting.objects.first()

    if date_str:
        try:
            att_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            att_date = timezone.localtime(timezone.now()).date()
    else:
        att_date = timezone.localtime(timezone.now()).date()

    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else ClassLevel.objects.first()
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    records = StudentAttendance.objects.filter(student__in=students, date=att_date)
    att_map = {r.student_id: r for r in records}
    for s in students:
        s.daily_record = att_map.get(s.id)
        s.current_status = s.daily_record.status if s.daily_record else "Present"

    return render(
        request,
        "students/student_daily_attendance_print.html",
        {
            "selected_class": selected_class,
            "selected_section": selected_section,
            "att_date": att_date,
            "students": students,
            "school_setting": school_setting,
        },
    )


# ==============================================================================
# CLASS-WISE MONTHLY ATTENDANCE SHEET (31-DAY MATRIX)
# ==============================================================================

@login_required
def student_monthly_attendance_sheet(request):
    """
    Interactive class-wise monthly attendance sheet matrix with days 1..31,
    per-student totals and overall class daily/monthly statistics.
    """
    classes = ClassLevel.objects.prefetch_related("sections").all()
    selected_class_id = request.GET.get("class_id") or (str(classes.first().id) if classes.exists() else "")
    selected_class = ClassLevel.objects.filter(id=selected_class_id).first() if selected_class_id else None

    sections = selected_class.sections.all() if selected_class else Section.objects.none()
    selected_section_id = request.GET.get("section_id") or ""
    selected_section = Section.objects.filter(id=selected_section_id).first() if selected_section_id else None

    now = timezone.localtime(timezone.now())
    month = int(request.GET.get("month", now.month))
    year = int(request.GET.get("year", now.year))

    _, num_days = calendar.monthrange(year, month)
    days_range = list(range(1, num_days + 1))

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    # Fetch all records for this month
    records = StudentAttendance.objects.filter(
        student__in=students,
        date__year=year,
        date__month=month,
    ).select_related("student")

    # Map: student_id -> day -> status
    matrix_map = {}
    for r in records:
        matrix_map.setdefault(r.student_id, {})[r.date.day] = r.status

    student_rows = []
    daily_present_totals = {d: 0 for d in days_range}
    daily_absent_totals = {d: 0 for d in days_range}

    for idx, s in enumerate(students, start=1):
        day_cells = []
        p_cnt, a_cnt, l_cnt, lv_cnt = 0, 0, 0, 0
        s_map = matrix_map.get(s.id, {})

        for d in days_range:
            st = s_map.get(d)
            if st in ["Present", "Late"]:
                p_cnt += 1
                daily_present_totals[d] += 1
                badge = "P"
                css = "cell-p"
            elif st == "Absent":
                a_cnt += 1
                daily_absent_totals[d] += 1
                badge = "A"
                css = "cell-a"
            elif st == "Leave":
                lv_cnt += 1
                badge = "Lv"
                css = "cell-lv"
            else:
                badge = "-"
                css = "cell-none"
            day_cells.append({"day": d, "status": st, "badge": badge, "css": css})

        total_marked = p_cnt + a_cnt
        pct = round((p_cnt / total_marked * 100), 1) if total_marked > 0 else 0.0

        student_rows.append({
            "serial": idx,
            "student": s,
            "day_cells": day_cells,
            "present_count": p_cnt,
            "absent_count": a_cnt,
            "leave_count": lv_cnt,
            "percentage": pct,
        })

    daily_totals_list = [
        {"day": d, "present": daily_present_totals[d], "absent": daily_absent_totals[d]}
        for d in days_range
    ]
    month_name = calendar.month_name[month]

    return render(
        request,
        "students/student_monthly_attendance_sheet.html",
        {
            "classes": classes,
            "sections": sections,
            "selected_class": selected_class,
            "selected_section": selected_section,
            "selected_class_id": selected_class_id,
            "selected_section_id": selected_section_id,
            "month": month,
            "year": year,
            "month_name": month_name,
            "days_range": days_range,
            "student_rows": student_rows,
            "daily_totals_list": daily_totals_list,
            "total_students": len(students),
        },
    )


@login_required
def student_monthly_attendance_print(request):
    """
    Printable monthly attendance grid for classroom records.
    """
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    now = timezone.localtime(timezone.now())
    month = int(request.GET.get("month", now.month))
    year = int(request.GET.get("year", now.year))

    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else ClassLevel.objects.first()
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None
    school_setting = SchoolSetting.objects.first()

    _, num_days = calendar.monthrange(year, month)
    days_range = list(range(1, num_days + 1))

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    records = StudentAttendance.objects.filter(
        student__in=students,
        date__year=year,
        date__month=month,
    )
    matrix_map = {}
    for r in records:
        matrix_map.setdefault(r.student_id, {})[r.date.day] = r.status

    student_rows = []
    for idx, s in enumerate(students, start=1):
        s_days = {}
        p_cnt, a_cnt, lv_cnt = 0, 0, 0
        s_map = matrix_map.get(s.id, {})
        for d in days_range:
            st = s_map.get(d)
            s_days[d] = st
            if st in ["Present", "Late"]:
                p_cnt += 1
            elif st == "Absent":
                a_cnt += 1
            elif st == "Leave":
                lv_cnt += 1
        tot = p_cnt + a_cnt
        pct = round((p_cnt / tot * 100), 1) if tot > 0 else 0.0
        student_rows.append({
            "serial": idx,
            "student": s,
            "days": s_days,
            "present_count": p_cnt,
            "absent_count": a_cnt,
            "leave_count": lv_cnt,
            "percentage": pct,
        })

    month_name = calendar.month_name[month]

    return render(
        request,
        "students/student_monthly_attendance_print.html",
        {
            "selected_class": selected_class,
            "selected_section": selected_section,
            "month": month,
            "year": year,
            "month_name": month_name,
            "days_range": days_range,
            "student_rows": student_rows,
            "school_setting": school_setting,
        },
    )


@login_required
def export_student_monthly_attendance_excel(request):
    """
    Excel export of monthly student attendance matrix.
    """
    from school.excel_utils import create_styled_workbook, excel_download_response

    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    now = timezone.localtime(timezone.now())
    month = int(request.GET.get("month", now.month))
    year = int(request.GET.get("year", now.year))

    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else None
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    _, num_days = calendar.monthrange(year, month)
    days_range = list(range(1, num_days + 1))

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    records = StudentAttendance.objects.filter(
        student__in=students,
        date__year=year,
        date__month=month,
    )
    matrix_map = {}
    for r in records:
        matrix_map.setdefault(r.student_id, {})[r.date.day] = r.status

    month_name = calendar.month_name[month]
    headers = ["S#", "Adm #", "Student Name", "Father Name", "Gender"] + [str(d) for d in days_range] + ["Present", "Absent", "Leave", "Att %"]

    rows = []
    for idx, s in enumerate(students, start=1):
        s_map = matrix_map.get(s.id, {})
        row = [idx, s.admission_no, s.full_name, s.father_name, s.gender]
        p_cnt, a_cnt, lv_cnt = 0, 0, 0
        for d in days_range:
            st = s_map.get(d)
            if st in ["Present", "Late"]:
                row.append("P")
                p_cnt += 1
            elif st == "Absent":
                row.append("A")
                a_cnt += 1
            elif st == "Leave":
                row.append("L")
                lv_cnt += 1
            else:
                row.append("-")
        tot = p_cnt + a_cnt
        pct = f"{round((p_cnt / tot * 100), 1)}%" if tot > 0 else "0%"
        row.extend([p_cnt, a_cnt, lv_cnt, pct])
        rows.append(row)

    title = f"Attendance {selected_class.name if selected_class else ''} - {month_name} {year}"
    buf = create_styled_workbook(title, headers, rows)
    return excel_download_response(buf, f"Student_Attendance_{month_name}_{year}.xlsx")


# ==============================================================================
# STUDENT YEARLY ATTENDANCE SHEET (END-OF-YEAR ANNUAL SUMS)
# ==============================================================================

@login_required
def student_yearly_attendance_sheet(request):
    """
    Yearly attendance summary sheet showing 12 monthly sums (Jan..Dec)
    and end-of-year final totals and percentages for each student.
    """
    classes = ClassLevel.objects.prefetch_related("sections").all()
    selected_class_id = request.GET.get("class_id") or (str(classes.first().id) if classes.exists() else "")
    selected_class = ClassLevel.objects.filter(id=selected_class_id).first() if selected_class_id else None

    sections = selected_class.sections.all() if selected_class else Section.objects.none()
    selected_section_id = request.GET.get("section_id") or ""
    selected_section = Section.objects.filter(id=selected_section_id).first() if selected_section_id else None

    now = timezone.localtime(timezone.now())
    year = int(request.GET.get("year", now.year))

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    # Fetch all records for this entire year
    records = StudentAttendance.objects.filter(
        student__in=students,
        date__year=year,
    )

    # student_id -> month -> {present: X, absent: Y, leave: Z}
    yearly_map = {}
    for r in records:
        m = r.date.month
        m_dict = yearly_map.setdefault(r.student_id, {}).setdefault(m, {"p": 0, "a": 0, "lv": 0})
        if r.status in ["Present", "Late"]:
            m_dict["p"] += 1
        elif r.status == "Absent":
            m_dict["a"] += 1
        elif r.status == "Leave":
            m_dict["lv"] += 1

    months_list = list(range(1, 13))
    student_rows = []

    for idx, s in enumerate(students, start=1):
        month_cells = []
        tot_p, tot_a, tot_lv = 0, 0, 0
        s_data = yearly_map.get(s.id, {})

        for m in months_list:
            m_stats = s_data.get(m, {"p": 0, "a": 0, "lv": 0})
            tot_p += m_stats["p"]
            tot_a += m_stats["a"]
            tot_lv += m_stats["lv"]
            month_cells.append({
                "month": m,
                "month_name": calendar.month_abbr[m],
                "present": m_stats["p"],
                "absent": m_stats["a"],
                "leave": m_stats["lv"],
            })

        tot_held = tot_p + tot_a
        overall_pct = round((tot_p / tot_held * 100), 1) if tot_held > 0 else 0.0

        student_rows.append({
            "serial": idx,
            "student": s,
            "month_cells": month_cells,
            "total_present": tot_p,
            "total_absent": tot_a,
            "total_leave": tot_lv,
            "total_held": tot_held,
            "overall_pct": overall_pct,
        })

    month_names = [calendar.month_abbr[m] for m in months_list]

    return render(
        request,
        "students/student_yearly_attendance_sheet.html",
        {
            "classes": classes,
            "sections": sections,
            "selected_class": selected_class,
            "selected_section": selected_section,
            "selected_class_id": selected_class_id,
            "selected_section_id": selected_section_id,
            "year": year,
            "month_names": month_names,
            "months_list": months_list,
            "student_rows": student_rows,
            "total_students": len(students),
        },
    )


@login_required
def export_student_yearly_attendance_excel(request):
    """
    Excel export of yearly student attendance sums.
    """
    from school.excel_utils import create_styled_workbook, excel_download_response

    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    now = timezone.localtime(timezone.now())
    year = int(request.GET.get("year", now.year))

    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else None
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    students = []
    if selected_class:
        sqs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            sqs = sqs.filter(current_section=selected_section)
        students = list(sqs.order_by("admission_no"))

    records = StudentAttendance.objects.filter(student__in=students, date__year=year)
    yearly_map = {}
    for r in records:
        m = r.date.month
        m_dict = yearly_map.setdefault(r.student_id, {}).setdefault(m, {"p": 0, "a": 0, "lv": 0})
        if r.status in ["Present", "Late"]:
            m_dict["p"] += 1
        elif r.status == "Absent":
            m_dict["a"] += 1
        elif r.status == "Leave":
            m_dict["lv"] += 1

    month_abbrs = [calendar.month_abbr[m] for m in range(1, 13)]
    headers = ["S#", "Adm #", "Student Name", "Father Name", "Gender"] + month_abbrs + ["Total Present", "Total Absent", "Total Leave", "Annual %"]

    rows = []
    for idx, s in enumerate(students, start=1):
        s_data = yearly_map.get(s.id, {})
        row = [idx, s.admission_no, s.full_name, s.father_name, s.gender]
        tot_p, tot_a, tot_lv = 0, 0, 0
        for m in range(1, 13):
            st = s_data.get(m, {"p": 0, "a": 0, "lv": 0})
            p = st["p"]
            tot_p += p
            tot_a += st["a"]
            tot_lv += st["lv"]
            row.append(p if p > 0 else 0)
        tot_held = tot_p + tot_a
        pct = f"{round((tot_p / tot_held * 100), 1)}%" if tot_held > 0 else "0%"
        row.extend([tot_p, tot_a, tot_lv, pct])
        rows.append(row)

    title = f"Annual Attendance {selected_class.name if selected_class else ''} - {year}"
    buf = create_styled_workbook(title, headers, rows)
    return excel_download_response(buf, f"Annual_Attendance_{year}.xlsx")


@login_required
def student_fee_collection_list(request):
    """
    Simple Student Fee & Exam Fee Collection Register:
    - Filter by Class, Section, Academic Session
    - Customizable Fee Name (e.g. Examination Fee, Paper Money, Sports Fund)
    - Default Fee Amount (e.g. Rs. 500)
    - Clean columns: S#, Roll/Adm No, Student Name, Father Name, Class & Section, Fee Amount, Paid, Balance, Date & Signature
    - 1-Click Print Layout (Office Printer Ready) & Excel Export
    """
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    school_setting = SchoolSetting.objects.first()

    class_id = request.GET.get("class_id", "").strip()
    section_id = request.GET.get("section_id", "").strip()
    fee_title = request.GET.get("fee_title", "Examination Fee Collection").strip()
    if not fee_title:
        fee_title = "Examination Fee Collection"
    try:
        default_fee = Decimal(request.GET.get("fee_amount", "500").strip() or "500")
    except Exception:
        default_fee = Decimal("500")

    classes = ClassLevel.objects.all()
    sections = Section.objects.all()

    students = Student.objects.filter(status="Active")
    selected_class = None
    selected_section = None

    if class_id:
        selected_class = ClassLevel.objects.filter(id=class_id).first()
        if selected_class:
            students = students.filter(current_class=selected_class)
            sections = sections.filter(class_level=selected_class)

    if section_id:
        selected_section = Section.objects.filter(id=section_id).first()
        if selected_section:
            students = students.filter(current_section=selected_section)

    students = list(students.order_by("admission_no"))
    total_students = len(students)
    total_amount = total_students * default_fee

    is_print = request.GET.get("print") == "1"

    context = {
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "students": students,
        "active_session": active_session,
        "school_setting": school_setting,
        "fee_title": fee_title,
        "default_fee": default_fee,
        "total_students": total_students,
        "total_amount": total_amount,
        "is_print": is_print,
    }

    if is_print:
        return render(request, "students/fee_collection_print.html", context)
    return render(request, "students/fee_collection_list.html", context)


@login_required
def export_student_fee_collection_excel(request):
    """
    Exports clean, styled Excel workbook for Exam Fee or Student Fee Collection.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    school_setting = SchoolSetting.objects.first()

    class_id = request.GET.get("class_id", "").strip()
    section_id = request.GET.get("section_id", "").strip()
    fee_title = request.GET.get("fee_title", "Examination Fee Collection").strip() or "Examination Fee Collection"
    try:
        default_fee = Decimal(request.GET.get("fee_amount", "500").strip() or "500")
    except Exception:
        default_fee = Decimal("500")

    students = Student.objects.filter(status="Active")
    selected_class = None
    if class_id:
        selected_class = ClassLevel.objects.filter(id=class_id).first()
        if selected_class:
            students = students.filter(current_class=selected_class)
    if section_id:
        sec = Section.objects.filter(id=section_id).first()
        if sec:
            students = students.filter(current_section=sec)

    students = list(students.order_by("admission_no"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Fee Collection"

    school_name = school_setting.name if school_setting else "School Management"

    # Title Block
    ws.merge_cells("A1:J1")
    ws["A1"] = school_name
    ws["A1"].font = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells("A2:J2")
    ws["A2"] = f"{fee_title.upper()} REGISTER — {selected_class.name if selected_class else 'ALL CLASSES'} ({active_session.name if active_session else ''})"
    ws["A2"].font = Font(name="Calibri", size=12, bold=True, color="334155")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

    headers = [
        "S#", "Adm #", "Student Name", "Father Name", "Class & Section",
        "Payable (PKR)", "Paid Amount", "Balance Due", "Payment Date", "Signature / Remarks"
    ]

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    ws.row_dimensions[4].height = 24
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    current_row = 5
    for idx, s in enumerate(students, start=1):
        ws.row_dimensions[current_row].height = 20
        cls_sec = f"{s.current_class.name if s.current_class else ''} - {s.section.name if s.section else ''}".strip(" -")
        vals = [idx, s.admission_no, s.full_name, s.father_name, cls_sec, float(default_fee), "", "", "", ""]
        for c_idx, val in enumerate(vals, start=1):
            cell = ws.cell(row=current_row, column=c_idx, value=val)
            cell.font = Font(name="Calibri", size=10)
            cell.border = thin_border
            if c_idx in [1, 2, 6]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in [3, 4, 5]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")
        current_row += 1

    # Total Row
    ws.merge_cells(f"A{current_row}:E{current_row}")
    tot_cell = ws.cell(row=current_row, column=1, value=f"TOTAL ENROLLED STUDENTS: {len(students)}")
    tot_cell.font = Font(name="Calibri", size=11, bold=True)
    tot_cell.alignment = Alignment(horizontal="right", vertical="center")
    
    tot_fee = ws.cell(row=current_row, column=6, value=float(len(students) * default_fee))
    tot_fee.font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
    tot_fee.alignment = Alignment(horizontal="center", vertical="center")

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    filename = f"Fee_Collection_{selected_class.name if selected_class else 'All'}_{fee_title.replace(' ', '_')}.xlsx"
    resp = HttpResponse(out.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

