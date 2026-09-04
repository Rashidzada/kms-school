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
from .forms import FamilyHouseholdForm, SinglePromoteForm, StudentForm, StudentWithdrawForm
from .models import FamilyHousehold, PromotionHistory, Student


@login_required
def student_list(request):
    """
    Searchable, filterable student list (FR-3.3):
    Filters: class, section, status.
    Free-text search: full name, admission number, father's name, residence.
    """
    students = Student.objects.select_related(
        "current_class", "current_section", "family"
    ).all()

    query = request.GET.get("q", "").strip()
    class_id = request.GET.get("class", "")
    section_id = request.GET.get("section", "")
    status = request.GET.get("status", "")

    if query:
        students = students.filter(
            Q(full_name__icontains=query)
            | Q(admission_no__icontains=query)
            | Q(father_name__icontains=query)
            | Q(residence__icontains=query)
        )

    if class_id:
        students = students.filter(current_class_id=class_id)
    if section_id:
        students = students.filter(current_section_id=section_id)
    if status:
        students = students.filter(status=status)

    classes = ClassLevel.objects.all()
    sections = Section.objects.all()

    context = {
        "students": students,
        "classes": classes,
        "sections": sections,
        "query": query,
        "selected_class": class_id,
        "selected_section": section_id,
        "selected_status": status,
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
    Student profile detail page (FR-3.4) with fee ledger history and promotion history.
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

    context = {
        "student": student,
        "promotions": promotions,
        "ledgers": ledgers,
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
