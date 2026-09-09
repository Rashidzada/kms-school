import io
import os
import re
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from school.excel_utils import excel_download_response, get_thin_border
from school.models import AcademicSession, ClassLevel, SchoolSetting, Section
from students.models import Student

from .forms import ClassSubjectForm, ExamForm, SubjectForm
from .models import (
    ClassSubject,
    Exam,
    ExamMark,
    Subject,
    calculate_grade,
    get_position_suffix,
)


@login_required
def exam_dashboard(request):
    """
    Central Examination & Results Dashboard.
    """
    school_setting = SchoolSetting.objects.first()
    active_session = AcademicSession.objects.filter(is_active=True).first()
    exams = Exam.objects.select_related("session").all()
    classes = ClassLevel.objects.all().order_by("name")
    subjects = Subject.objects.all().order_by("order", "name")

    total_exams = exams.count()
    total_subjects = subjects.count()
    total_marks_recorded = ExamMark.objects.count()

    context = {
        "school_setting": school_setting,
        "active_session": active_session,
        "exams": exams,
        "classes": classes,
        "subjects": subjects,
        "total_exams": total_exams,
        "total_subjects": total_subjects,
        "total_marks_recorded": total_marks_recorded,
    }
    return render(request, "exams/exam_dashboard.html", context)


@login_required
def exam_list(request):
    """
    List and manage examinations.
    """
    exams = Exam.objects.select_related("session").all()
    return render(request, "exams/exam_list.html", {"exams": exams})


@login_required
def exam_create(request):
    """
    Create a new Examination term.
    """
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f"Examination '{exam.name}' created successfully.")
            return redirect("exam_list")
    else:
        active_session = AcademicSession.objects.filter(is_active=True).first()
        form = ExamForm(initial={"session": active_session, "is_active": True})

    return render(request, "exams/exam_form.html", {"form": form, "title": "Create Examination Term"})


@login_required
def exam_edit(request, pk):
    """
    Edit an existing examination.
    """
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Examination '{exam.name}' updated successfully.")
            return redirect("exam_list")
    else:
        form = ExamForm(instance=exam)

    return render(request, "exams/exam_form.html", {"form": form, "title": f"Edit Examination: {exam.name}"})


# ==============================================================================
# SUBJECT MANAGEMENT & CLASS-SUBJECT CONFIGURATION (INCREASE / DECREASE SUBJECTS)
# ==============================================================================

@login_required
def subject_manage(request):
    """
    Manage Master Subjects and Class-Subject assignments (Increase/Decrease subjects).
    """
    classes = ClassLevel.objects.all().order_by("name")
    selected_class_id = request.GET.get("class_id")

    selected_class = None
    if selected_class_id:
        selected_class = ClassLevel.objects.filter(id=selected_class_id).first()
    if not selected_class and classes.exists():
        selected_class = classes.first()

    class_subjects = []
    if selected_class:
        class_subjects = ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order", "subject__order")

    subjects = Subject.objects.all().order_by("order", "name")
    subject_form = SubjectForm()
    class_subject_form = ClassSubjectForm(initial={"class_level": selected_class})

    # Handle Actions
    if request.method == "POST":
        action = request.POST.get("action")

        # 1. Create a new master subject
        if action == "add_master_subject":
            s_form = SubjectForm(request.POST)
            if s_form.is_valid():
                s = s_form.save()
                messages.success(request, f"Subject '{s.name}' added to master catalog.")
                return redirect(f"{request.path}?class_id={selected_class.id if selected_class else ''}")
            else:
                messages.error(request, "Could not add subject. Check if the name already exists.")

        # 2. Assign subject to class (Increase subjects for this class)
        elif action == "add_class_subject":
            subject_id = request.POST.get("subject")
            total_marks = request.POST.get("total_marks", "100")
            passing_marks = request.POST.get("passing_marks", "33")
            order = request.POST.get("order", "0")

            if selected_class and subject_id:
                sub = get_object_or_404(Subject, id=subject_id)
                cs, created = ClassSubject.objects.get_or_create(
                    class_level=selected_class,
                    subject=sub,
                    defaults={
                        "total_marks": Decimal(total_marks),
                        "passing_marks": Decimal(passing_marks),
                        "order": int(order),
                    },
                )
                if not created:
                    cs.total_marks = Decimal(total_marks)
                    cs.passing_marks = Decimal(passing_marks)
                    cs.order = int(order)
                    cs.save()
                    messages.success(request, f"Updated subject '{sub.name}' for {selected_class.name}.")
                else:
                    messages.success(request, f"Added '{sub.name}' to {selected_class.name} with Max Marks {total_marks}.")
                return redirect(f"{request.path}?class_id={selected_class.id}")

        # 3. Remove subject from class (Decrease subjects for this class)
        elif action == "remove_class_subject":
            cs_id = request.POST.get("class_subject_id")
            if cs_id:
                cs = get_object_or_404(ClassSubject, id=cs_id)
                sub_name = cs.subject.name
                c_name = cs.class_level.name
                cs.delete()
                messages.warning(request, f"Subject '{sub_name}' removed from {c_name}.")
                return redirect(f"{request.path}?class_id={selected_class.id}")

        # 4. Auto-seed standard KP Board / Kohisar subjects for this class
        elif action == "seed_standard_subjects":
            if selected_class:
                seed_default_subjects_for_class(selected_class)
                messages.success(request, f"Standard curriculum subjects configured for {selected_class.name} successfully.")
                return redirect(f"{request.path}?class_id={selected_class.id}")

    context = {
        "classes": classes,
        "selected_class": selected_class,
        "class_subjects": class_subjects,
        "subjects": subjects,
        "subject_form": subject_form,
        "class_subject_form": class_subject_form,
    }
    return render(request, "exams/subject_manage.html", context)


def seed_default_subjects_for_class(class_level):
    """
    Configures standard subjects matching Kohisar Model School curriculum and Image 1.
    """
    # Master standard subjects catalog
    standard_catalog = [
        ("English", "Eng", 1),
        ("Urdu", "Urdu", 2),
        ("Mathematics", "Maths", 3),
        ("Pakistan Studies", "P.Study", 4),
        ("Islamyat", "Islamyat", 5),
        ("Biology", "Bio", 6),
        ("Chemistry", "Che", 7),
        ("Physics", "Phy", 8),
        ("Mutalae Quran", "M.quran", 9),
        ("Computer Science", "CS", 10),
        ("General Science", "G.Sci", 11),
        ("Pashto", "Pashto", 12),
        ("Drawing / Art", "Drawing", 13),
        ("General Knowledge", "GK", 14),
        ("Nazra Quran", "Nazra", 15),
    ]

    master_subjects = {}
    for name, code, order in standard_catalog:
        sub, _ = Subject.objects.get_or_create(
            name=name,
            defaults={"code": code, "order": order, "is_active": True},
        )
        master_subjects[code] = sub

    cname = class_level.name.lower()

    if any(k in cname for k in ["9", "10", "pre-medical", "pre-engineering", "ics"]):
        # Secondary / High School setup (Exact match to Image 1: 650 Grand Total)
        curriculum = [
            ("Eng", 75, 25, 1),
            ("Urdu", 75, 25, 2),
            ("Maths", 75, 25, 3),
            ("P.Study", 75, 25, 4),
            ("Islamyat", 50, 17, 5),
            ("Bio", 75, 25, 6),
            ("Che", 75, 25, 7),
            ("Phy", 75, 25, 8),
            ("M.quran", 50, 17, 9),
        ]
    elif any(k in cname for k in ["nursery", "prep", "kg"]):
        # Nursery / KG setup
        curriculum = [
            ("Eng", 100, 33, 1),
            ("Urdu", 100, 33, 2),
            ("Maths", 100, 33, 3),
            ("GK", 50, 17, 4),
            ("Nazra", 50, 17, 5),
            ("Drawing", 50, 17, 6),
        ]
    else:
        # Primary & Middle (Class 1 to 8)
        curriculum = [
            ("Eng", 100, 33, 1),
            ("Urdu", 100, 33, 2),
            ("Maths", 100, 33, 3),
            ("G.Sci", 100, 33, 4),
            ("Islamyat", 50, 17, 5),
            ("P.Study", 50, 17, 6),
            ("M.quran", 50, 17, 7),
            ("Pashto", 50, 17, 8),
        ]

    for code, total_m, pass_m, order in curriculum:
        sub = master_subjects.get(code)
        if sub:
            ClassSubject.objects.update_or_create(
                class_level=class_level,
                subject=sub,
                defaults={
                    "total_marks": Decimal(total_m),
                    "passing_marks": Decimal(pass_m),
                    "order": order,
                },
            )


# ==============================================================================
# FEATURE 2: SUBJECT AWARD LIST / PAPER MARKS SHEET (IMAGE 2)
# ==============================================================================

@login_required
def subject_award_sheet(request):
    """
    Teacher's Subject Award List (Image 2 format: S#no, NAME, F/NAME, T/MARKS, O/MARKS).
    Enables online marks entry, Excel export/import, and official printable award list.
    """
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    subject_id = request.GET.get("subject_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    # Get class subjects for this class
    class_subjects = ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order") if selected_class else []

    selected_subject = None
    if subject_id:
        selected_subject = Subject.objects.filter(id=subject_id).first()
    elif class_subjects.exists():
        selected_subject = class_subjects.first().subject

    # Current class-subject configuration for total marks
    current_cs = None
    if selected_class and selected_subject:
        current_cs = ClassSubject.objects.filter(class_level=selected_class, subject=selected_subject).first()

    default_total_marks = current_cs.total_marks if current_cs else Decimal("100.0")

    # Fetch active students
    students = []
    student_rows = []
    if selected_class:
        students_qs = Student.objects.filter(current_class=selected_class, status="Active").order_by("admission_no")
        if selected_section:
            students_qs = students_qs.filter(current_section=selected_section)
        students = list(students_qs)

        # Existing marks map
        existing_marks = {}
        if selected_exam and selected_subject:
            marks_qs = ExamMark.objects.filter(
                exam=selected_exam,
                class_level=selected_class,
                subject=selected_subject,
                student__in=students,
            )
            for m in marks_qs:
                existing_marks[m.student_id] = m

        # Handle POST Save Marks directly from web table
        if request.method == "POST" and request.POST.get("action") == "save_marks":
            saved_count = 0
            with transaction.atomic():
                for s in students:
                    obtained_val = request.POST.get(f"obtained_{s.id}", "").strip()
                    is_absent = request.POST.get(f"absent_{s.id}") == "1"

                    if is_absent:
                        ExamMark.objects.update_or_create(
                            exam=selected_exam,
                            student=s,
                            subject=selected_subject,
                            defaults={
                                "class_level": selected_class,
                                "total_marks": default_total_marks,
                                "obtained_marks": Decimal("0.0"),
                                "is_absent": True,
                            },
                        )
                        saved_count += 1
                    elif obtained_val != "":
                        try:
                            obt_dec = Decimal(obtained_val)
                            obt_dec = min(obt_dec, default_total_marks)
                            obt_dec = max(obt_dec, Decimal("0.0"))
                            ExamMark.objects.update_or_create(
                                exam=selected_exam,
                                student=s,
                                subject=selected_subject,
                                defaults={
                                    "class_level": selected_class,
                                    "total_marks": default_total_marks,
                                    "obtained_marks": obt_dec,
                                    "is_absent": False,
                                },
                            )
                            saved_count += 1
                        except Exception:
                            continue

            messages.success(
                request,
                f"Successfully saved marks for {saved_count} students in {selected_subject.name} ({selected_class.name}).",
            )
            return redirect(
                f"{request.path}?exam_id={selected_exam.id if selected_exam else ''}&class_id={selected_class.id if selected_class else ''}&section_id={selected_section.id if selected_section else ''}&subject_id={selected_subject.id if selected_subject else ''}"
            )

        # Build student rows for template
        for idx, s in enumerate(students, start=1):
            mark_obj = existing_marks.get(s.id)
            student_rows.append({
                "sr_no": idx,
                "student": s,
                "total_marks": int(default_total_marks) if default_total_marks % 1 == 0 else default_total_marks,
                "obtained_marks": mark_obj.display_score if mark_obj else "",
                "is_absent": mark_obj.is_absent if mark_obj else False,
                "mark_obj": mark_obj,
            })

    context = {
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "class_subjects": class_subjects,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "selected_subject": selected_subject,
        "current_cs": current_cs,
        "default_total_marks": int(default_total_marks) if default_total_marks % 1 == 0 else default_total_marks,
        "student_rows": student_rows,
        "total_students": len(students),
    }
    return render(request, "exams/subject_award_sheet.html", context)


@login_required
def export_subject_award_excel(request):
    """
    Exports single-subject Award Sheet template in Excel format (matching Image 2).
    Pre-populates Student Name & Father Name for teachers to fill via Excel/Google Sheets.
    """
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    subject_id = request.GET.get("subject_id")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    section = Section.objects.filter(id=section_id).first() if section_id else None

    cs = ClassSubject.objects.filter(class_level=class_level, subject=subject).first()
    total_marks = int(cs.total_marks) if cs and cs.total_marks % 1 == 0 else (cs.total_marks if cs else 100)

    students_qs = Student.objects.filter(current_class=class_level, status="Active").order_by("admission_no")
    if section:
        students_qs = students_qs.filter(current_section=section)

    existing_marks = {
        m.student_id: m
        for m in ExamMark.objects.filter(exam=exam, class_level=class_level, subject=subject)
    }

    wb = Workbook()
    ws = wb.active
    ws.title = f"{subject.short_name[:10]}_{class_level.name[:10]}"

    # Header title banner matching Image 2
    school_name = "KOHISAR MODEL SCHOOL AND COLLEGE QALAGAY SWAT"
    subtitle = f"LIST FOR {subject.name.upper()} PAPER CLASS {class_level.name.upper()}  —  {exam.name.upper()}"
    if section:
        subtitle += f" (SECTION {section.name})"

    ws.merge_cells("A1:F1")
    ws["A1"] = school_name
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1A365D")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:F2")
    ws["A2"] = subtitle
    ws["A2"].font = Font(name="Arial", size=11, bold=True, color="2B6CB0")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # Embed school logo if available
    logo_file = os.path.join(settings.BASE_DIR, "static", "dist", "img", "logo.png")
    if os.path.exists(logo_file):
        try:
            from openpyxl.drawing.image import Image as XLImage
            xl_img = XLImage(logo_file)
            xl_img.width = 46
            xl_img.height = 46
            ws.add_image(xl_img, "A1")
        except Exception:
            pass

    # Column Headers
    headers = ["S#no", "Admission #", "NAME", "F/NAME", "T/ MARKS", "O/MARKS"]
    header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    border = get_thin_border()

    for col_idx, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=col_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border
    ws.row_dimensions[3].height = 25

    # Data Rows
    data_font = Font(name="Arial", size=10)
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    for row_idx, s in enumerate(students_qs, start=4):
        sr = row_idx - 3
        m = existing_marks.get(s.id)
        obt_val = ""
        if m:
            obt_val = "A" if m.is_absent else (int(m.obtained_marks) if m.obtained_marks % 1 == 0 else float(m.obtained_marks))

        row_vals = [sr, s.admission_no, s.full_name, s.father_name, total_marks, obt_val]
        is_alt = (row_idx % 2 == 0)

        for col_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = data_font
            cell.border = border
            if is_alt:
                cell.fill = alt_fill

            if col_idx in [1, 2, 5]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 6:
                # Obtained marks column highlighted for teachers
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.font = Font(name="Arial", size=10, bold=True, color="000000")
                cell.fill = PatternFill(start_color="FEFCBF", end_color="FEFCBF", fill_type="solid")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        ws.row_dimensions[row_idx].height = 20

    # Auto column widths
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["D"].width = 26
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 14

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"AwardSheet_{class_level.name}_{subject.short_name}_{exam.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)


@login_required
def import_subject_award_excel(request):
    """
    Imports filled Subject Award Sheet Excel file from teacher.
    """
    if request.method != "POST":
        return redirect("subject_award_sheet")

    exam_id = request.POST.get("exam_id")
    class_id = request.POST.get("class_id")
    subject_id = request.POST.get("subject_id")
    uploaded_file = request.FILES.get("excel_file")

    if not (exam_id and class_id and subject_id and uploaded_file):
        messages.error(request, "Missing exam, class, subject, or Excel file.")
        return redirect("subject_award_sheet")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)

    cs = ClassSubject.objects.filter(class_level=class_level, subject=subject).first()
    max_marks = cs.total_marks if cs else Decimal("100.0")

    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {str(e)}")
        return redirect(f"subject_award_sheet?exam_id={exam.id}&class_id={class_level.id}&subject_id={subject.id}")

    # Find header row (contains "name" or "o/marks" or "admission")
    header_idx = -1
    for idx, r in enumerate(rows[:10]):
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if "name" in row_str and ("marks" in row_str or "o/marks" in row_str or "s#no" in row_str):
            header_idx = idx
            break

    if header_idx == -1:
        messages.error(request, "Could not find valid column headers in the uploaded Excel file.")
        return redirect(f"subject_award_sheet?exam_id={exam.id}&class_id={class_level.id}&subject_id={subject.id}")

    raw_headers = [str(c).strip().lower() if c is not None else "" for c in rows[header_idx]]

    adm_col = -1
    name_col = -1
    fname_col = -1
    obt_col = -1

    for c_idx, h in enumerate(raw_headers):
        if "admission" in h:
            adm_col = c_idx
        elif "name" in h and "father" not in h and "f/name" not in h:
            name_col = c_idx
        elif "f/name" in h or "father" in h:
            fname_col = c_idx
        elif "o/marks" in h or "obtained" in h or (c_idx == len(raw_headers) - 1 and "mark" in h):
            obt_col = c_idx

    # Fallback column indices if standard template
    if obt_col == -1 and len(raw_headers) >= 6:
        obt_col = 5
    if adm_col == -1 and len(raw_headers) >= 2:
        adm_col = 1
    if name_col == -1 and len(raw_headers) >= 3:
        name_col = 2

    # Map existing students in this class
    class_students = Student.objects.filter(current_class=class_level)
    student_by_adm = {s.admission_no.strip().lower(): s for s in class_students if s.admission_no}
    student_by_name = {s.full_name.strip().lower(): s for s in class_students}

    updated_count = 0
    skipped_count = 0
    errors = []

    with transaction.atomic():
        for r_idx, row_values in enumerate(rows[header_idx + 1:], start=header_idx + 2):
            if not any(row_values):
                continue

            target_student = None
            adm_val = str(row_values[adm_col]).strip() if adm_col != -1 and adm_col < len(row_values) and row_values[adm_col] else ""
            name_val = str(row_values[name_col]).strip() if name_col != -1 and name_col < len(row_values) and row_values[name_col] else ""
            fname_val = str(row_values[fname_col]).strip() if fname_col != -1 and fname_col < len(row_values) and row_values[fname_col] else ""

            if adm_val:
                target_student = student_by_adm.get(adm_val.lower())
                if not target_student:
                    # Check globally across school
                    target_student = Student.objects.filter(admission_no__iexact=adm_val).first()
                    if target_student and target_student.current_class != class_level:
                        target_student.current_class = class_level
                        target_student.save(update_fields=["current_class"])

            if not target_student and name_val:
                target_student = student_by_name.get(name_val.lower())
                if not target_student:
                    # Check globally by name
                    target_student = Student.objects.filter(full_name__iexact=name_val).first()
                    if target_student and target_student.current_class != class_level:
                        target_student.current_class = class_level
                        target_student.save(update_fields=["current_class"])

            # If student is brand new, auto-add to this class and to the result
            if not target_student and name_val:
                default_section = Section.objects.filter(class_level=class_level).first()
                target_student = Student(
                    full_name=name_val,
                    father_name=fname_val or "Guardian",
                    current_class=class_level,
                    current_section=default_section,
                    status="Active",
                )
                if adm_val and not Student.objects.filter(admission_no=adm_val).exists():
                    target_student.admission_no = adm_val
                target_student.save()
                student_by_adm[target_student.admission_no.lower()] = target_student
                student_by_name[target_student.full_name.lower()] = target_student

            if not target_student:
                skipped_count += 1
                continue

            # Parse obtained marks
            obt_raw = row_values[obt_col] if obt_col != -1 and obt_col < len(row_values) else None
            if obt_raw is None or str(obt_raw).strip() == "":
                continue

            obt_str = str(obt_raw).strip().upper()
            if obt_str in ["A", "ABS", "ABSENT"]:
                ExamMark.objects.update_or_create(
                    exam=exam,
                    student=target_student,
                    subject=subject,
                    defaults={
                        "class_level": class_level,
                        "total_marks": max_marks,
                        "obtained_marks": Decimal("0.0"),
                        "is_absent": True,
                    },
                )
                updated_count += 1
            else:
                try:
                    num_val = Decimal(re.sub(r"[^\d.]", "", obt_str))
                    num_val = min(num_val, max_marks)
                    num_val = max(num_val, Decimal("0.0"))
                    ExamMark.objects.update_or_create(
                        exam=exam,
                        student=target_student,
                        subject=subject,
                        defaults={
                            "class_level": class_level,
                            "total_marks": max_marks,
                            "obtained_marks": num_val,
                            "is_absent": False,
                        },
                    )
                    updated_count += 1
                except Exception as e:
                    errors.append(f"Row {r_idx}: Invalid marks '{obt_raw}' for {target_student.full_name}")

    if updated_count > 0:
        messages.success(request, f"Successfully imported and updated marks for {updated_count} students in {subject.name}!")
    if skipped_count > 0:
        messages.info(request, f"{skipped_count} rows were skipped (unmatched student name or blank rows).")
    if errors:
        messages.warning(request, f"Some rows had issues: {'; '.join(errors[:3])}")

    return redirect(f"{request.path.replace('import-award-excel/', '')}?exam_id={exam.id}&class_id={class_level.id}&subject_id={subject.id}")


@login_required
def print_subject_award_sheet(request):
    """
    Dedicated printable view matching Image 2 (`media_1788918980136.jpg`).
    """
    school_setting = SchoolSetting.objects.first()
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")
    subject_id = request.GET.get("subject_id")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    section = Section.objects.filter(id=section_id).first() if section_id else None

    cs = ClassSubject.objects.filter(class_level=class_level, subject=subject).first()
    default_total = int(cs.total_marks) if cs and cs.total_marks % 1 == 0 else (cs.total_marks if cs else 100)

    students_qs = Student.objects.filter(current_class=class_level, status="Active").order_by("admission_no")
    if section:
        students_qs = students_qs.filter(current_section=section)

    existing_marks = {
        m.student_id: m
        for m in ExamMark.objects.filter(exam=exam, class_level=class_level, subject=subject)
    }

    student_rows = []
    for idx, s in enumerate(students_qs, start=1):
        m = existing_marks.get(s.id)
        student_rows.append({
            "sr_no": idx,
            "student": s,
            "total_marks": default_total,
            "obtained_marks": m.display_score if m else "",
            "is_absent": m.is_absent if m else False,
        })

    context = {
        "school_setting": school_setting,
        "exam": exam,
        "class_level": class_level,
        "section": section,
        "subject": subject,
        "default_total": default_total,
        "student_rows": student_rows,
        "total_students": len(student_rows),
    }
    return render(request, "exams/print_subject_award.html", context)


# ==============================================================================
# FEATURE 1: MASTER CLASS RESULT SHEET (IMAGE 1)
# ==============================================================================

def compute_class_result_matrix(exam, class_level, section=None):
    """
    Computes complete result matrix for a class:
    - Dynamic subject columns with max marks
    - Student rows with marks in each subject
    - Grand Total Obtained / Max Total
    - Percentage
    - Positions (1st, 2nd, 3rd) with tie resolution
    - Grade (A+, A, B, C, D, E, Fail)
    - Pass/Fail Status
    - Class Summary Statistics
    """
    # 1. Get class subjects ordered
    class_subjects = list(
        ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
    )
    if not class_subjects:
        # If none exist yet, automatically seed standard curriculum
        seed_default_subjects_for_class(class_level)
        class_subjects = list(
            ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
        )

    grand_total_max = sum(cs.total_marks for cs in class_subjects)

    # 2. Get students
    students_qs = Student.objects.filter(current_class=class_level, status="Active").order_by("admission_no")
    if section:
        students_qs = students_qs.filter(current_section=section)
    students = list(students_qs)

    # 3. Get all marks for this exam and class
    marks_qs = ExamMark.objects.filter(
        exam=exam,
        class_level=class_level,
        student__in=students,
    ).select_related("subject")

    marks_map = {}  # (student_id, subject_id) -> ExamMark
    for m in marks_qs:
        marks_map[(m.student_id, m.subject_id)] = m

    # 4. Build student rows
    student_records = []
    for s in students:
        subject_marks_list = []
        obtained_total = Decimal("0.0")
        has_failed_subject = False
        all_absent = True
        has_any_mark = False

        for cs in class_subjects:
            m = marks_map.get((s.id, cs.subject_id))
            if m:
                has_any_mark = True
                if m.is_absent:
                    score_disp = "A"
                    has_failed_subject = True
                else:
                    all_absent = False
                    score_disp = int(m.obtained_marks) if m.obtained_marks % 1 == 0 else m.obtained_marks
                    obtained_total += m.obtained_marks
                    if m.obtained_marks < cs.passing_marks:
                        has_failed_subject = True
            else:
                score_disp = ""

            subject_marks_list.append({
                "class_subject": cs,
                "score_display": score_disp,
                "mark_obj": m,
            })

        # Calculate percentage
        if grand_total_max > 0 and not all_absent and has_any_mark:
            percentage = round((float(obtained_total) / float(grand_total_max)) * 100, 2)
            grade = calculate_grade(percentage)
            status = "Fail" if (has_failed_subject or percentage < 33.0) else "Pass"
        else:
            percentage = 0.0 if has_any_mark else None
            grade = "Fail" if has_any_mark else ""
            status = "Fail" if has_any_mark else "Pending"

        student_records.append({
            "student": s,
            "subject_marks": subject_marks_list,
            "obtained_total": (int(obtained_total) if obtained_total % 1 == 0 else obtained_total) if has_any_mark else "",
            "obtained_total_num": float(obtained_total),
            "percentage": percentage,
            "grade": grade,
            "status": status,
            "has_any_mark": has_any_mark,
            "all_absent": all_absent,
            "position": None,
            "position_display": "",
        })

    # 5. Compute Positions / Ranks (Sorted by Total Obtained descending)
    # Only students with marks and not all-absent compete for positions
    valid_students = [rec for rec in student_records if rec["has_any_mark"] and not rec["all_absent"]]
    valid_students.sort(key=lambda x: x["obtained_total_num"], reverse=True)

    current_rank = 1
    for idx, rec in enumerate(valid_students):
        if idx > 0 and rec["obtained_total_num"] == valid_students[idx - 1]["obtained_total_num"]:
            # Same marks as previous -> same position (tie)
            rec["position"] = valid_students[idx - 1]["position"]
        else:
            rec["position"] = idx + 1
        rec["position_display"] = get_position_suffix(rec["position"])

    # Put back in admission_no order for display
    student_records.sort(key=lambda x: x["student"].admission_no)
    for idx, rec in enumerate(student_records, start=1):
        rec["sr_no"] = idx

    # 6. Compute Class Summary Statistics
    total_enrolled = len(student_records)
    total_appeared = len(valid_students)
    passed_count = sum(1 for rec in valid_students if rec["status"] == "Pass")
    failed_count = sum(1 for rec in valid_students if rec["status"] == "Fail")
    pass_percentage = round((passed_count / total_appeared) * 100, 1) if total_appeared > 0 else 0.0
    highest_marks = max([rec["obtained_total_num"] for rec in valid_students], default=0.0)
    avg_marks = round(sum([rec["obtained_total_num"] for rec in valid_students]) / total_appeared, 1) if total_appeared > 0 else 0.0

    stats = {
        "total_enrolled": total_enrolled,
        "total_appeared": total_appeared,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "pass_percentage": pass_percentage,
        "highest_marks": int(highest_marks) if highest_marks % 1 == 0 else highest_marks,
        "avg_marks": avg_marks,
    }

    return class_subjects, grand_total_max, student_records, stats


@login_required
def class_result_sheet(request):
    """
    Master Class Result Sheet (Image 1 format).
    Displays multi-subject results, Grand Total, %age, Position, and Grade.
    """
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = []
    grand_total_max = 0
    student_records = []
    stats = {}

    if selected_exam and selected_class:
        class_subjects, grand_total_max, student_records, stats = compute_class_result_matrix(
            selected_exam, selected_class, selected_section
        )

    context = {
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "class_subjects": class_subjects,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
        "student_records": student_records,
        "stats": stats,
    }
    return render(request, "exams/class_result_sheet.html", context)


@login_required
def export_class_result_excel(request):
    """
    Exports full multi-subject Class Result Sheet to Excel matching Image 1.
    """
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects, grand_total_max, student_records, stats = compute_class_result_matrix(
        exam, class_level, section
    )

    wb = Workbook()
    ws = wb.active
    ws.title = f"Result_{class_level.name[:12]}"

    # Header title banner
    school_name = "KOHISAR MODEL SCHOOL & COLLEGE QALAGAY SWAT"
    sub_title = f"Result Sheet For Class: {class_level.name}   —   {exam.name}"
    if section:
        sub_title += f" (Section: {section.name})"

    # Total columns = Sr No + Name + Father's Name + len(subjects) + G.Total + %age + Position + Grade
    total_cols = 3 + len(class_subjects) + 4

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    ws["A1"] = school_name
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1A365D")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    ws["A2"] = sub_title
    ws["A2"].font = Font(name="Arial", size=11, bold=True, color="2B6CB0")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 24

    # Embed school logo if available
    logo_file = os.path.join(settings.BASE_DIR, "static", "dist", "img", "logo.png")
    if os.path.exists(logo_file):
        try:
            from openpyxl.drawing.image import Image as XLImage
            xl_img = XLImage(logo_file)
            xl_img.width = 46
            xl_img.height = 46
            ws.add_image(xl_img, "A1")
        except Exception:
            pass

    # Table Column Headers
    headers = ["Sr No", "Name", "Father's Name"]
    for cs in class_subjects:
        headers.append(cs.header_label)

    gt_max_str = int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max
    headers.extend([f"G.Total ({gt_max_str})", "%age", "Position", "Grade"])

    header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    border = get_thin_border()

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws.row_dimensions[3].height = 28

    # Data Rows
    data_font = Font(name="Arial", size=10)
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    for row_idx, rec in enumerate(student_records, start=4):
        is_alt = (row_idx % 2 == 0)
        row_vals = [
            rec["sr_no"],
            rec["student"].full_name,
            rec["student"].father_name,
        ]
        for sm in rec["subject_marks"]:
            row_vals.append(sm["score_display"])

        row_vals.extend([
            rec["obtained_total"] if rec["has_any_mark"] else "",
            f"{rec['percentage']}%" if (rec["percentage"] is not None and rec["has_any_mark"]) else "",
            rec["position_display"],
            rec["grade"],
        ])

        for col_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = data_font
            cell.border = border
            if is_alt:
                cell.fill = alt_fill

            if col_idx in [1]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [2, 3]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.row_dimensions[row_idx].height = 20

    # Auto column widths
    ws.column_dimensions["A"].width = 7
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 24
    for idx in range(4, 4 + len(class_subjects)):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = 12
    ws.column_dimensions[get_column_letter(4 + len(class_subjects))].width = 14
    ws.column_dimensions[get_column_letter(5 + len(class_subjects))].width = 10
    ws.column_dimensions[get_column_letter(6 + len(class_subjects))].width = 11
    ws.column_dimensions[get_column_letter(7 + len(class_subjects))].width = 10

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"Result_Sheet_{class_level.name}_{exam.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)


@login_required
def print_class_result_sheet(request):
    """
    Printable landscape Result Sheet matching Image 1 (`media_1788918965518.jpg`).
    """
    school_setting = SchoolSetting.objects.first()
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects, grand_total_max, student_records, stats = compute_class_result_matrix(
        exam, class_level, section
    )

    context = {
        "school_setting": school_setting,
        "exam": exam,
        "class_level": class_level,
        "section": section,
        "class_subjects": class_subjects,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
        "student_records": student_records,
        "stats": stats,
    }
    return render(request, "exams/print_class_result.html", context)


@login_required
def student_dmc(request, student_id, exam_id):
    """
    Detailed Marks Certificate (DMC / Report Card) for a single student.
    """
    school_setting = SchoolSetting.objects.first()
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    class_level = student.current_class

    class_subjects, grand_total_max, student_records, stats = compute_class_result_matrix(
        exam, class_level, student.current_section
    )

    # Find this student's computed record
    student_rec = None
    for rec in student_records:
        if rec["student"].id == student.id:
            student_rec = rec
            break

    context = {
        "school_setting": school_setting,
        "student": student,
        "exam": exam,
        "class_level": class_level,
        "student_rec": student_rec,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
    }
    return render(request, "exams/student_dmc.html", context)


# ==============================================================================
# MULTI-SUBJECT CLASS MARKS ENTRY GRID (SPREADSHEET-STYLE LIVE ENTRY)
# ==============================================================================

@login_required
def class_marks_entry_grid(request):
    """
    Spreadsheet-like Multi-Subject Marks Entry Grid.
    Allows entering and updating marks across all subjects for all students of a class simultaneously.
    """
    school_setting = SchoolSetting.objects.first()
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id") or request.POST.get("exam_id")
    class_id = request.GET.get("class_id") or request.POST.get("class_id")
    section_id = request.GET.get("section_id") or request.POST.get("section_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = []
    students = []
    student_grid_rows = []

    if selected_class:
        class_subjects = list(
            ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order", "subject__order")
        )
        if not class_subjects:
            seed_default_subjects_for_class(selected_class)
            class_subjects = list(
                ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order", "subject__order")
            )

        students_qs = Student.objects.filter(current_class=selected_class, status="Active").order_by("admission_no")
        if selected_section:
            students_qs = students_qs.filter(current_section=selected_section)
        students = list(students_qs)

    # Handle POST - Save Grid Marks directly from web
    if request.method == "POST" and request.POST.get("action") == "save_grid_marks":
        saved_marks_count = 0
        with transaction.atomic():
            for s in students:
                for cs in class_subjects:
                    field_key = f"mark_{s.id}_{cs.subject_id}"
                    val = request.POST.get(field_key, "").strip()

                    if val.upper() in ["A", "ABS", "ABSENT"]:
                        ExamMark.objects.update_or_create(
                            exam=selected_exam,
                            student=s,
                            subject=cs.subject,
                            defaults={
                                "class_level": selected_class,
                                "total_marks": cs.total_marks,
                                "obtained_marks": Decimal("0.0"),
                                "is_absent": True,
                            }
                        )
                        saved_marks_count += 1
                    elif val != "":
                        try:
                            dec_val = Decimal(re.sub(r"[^\d.]", "", val))
                            dec_val = min(dec_val, cs.total_marks)
                            dec_val = max(dec_val, Decimal("0.0"))
                            ExamMark.objects.update_or_create(
                                exam=selected_exam,
                                student=s,
                                subject=cs.subject,
                                defaults={
                                    "class_level": selected_class,
                                    "total_marks": cs.total_marks,
                                    "obtained_marks": dec_val,
                                    "is_absent": False,
                                }
                            )
                            saved_marks_count += 1
                        except Exception:
                            continue

        messages.success(request, f"Successfully saved {saved_marks_count} marks entries for {len(students)} students in {selected_class.name}!")
        return redirect(f"{request.path}?exam_id={selected_exam.id}&class_id={selected_class.id}&section_id={selected_section.id if selected_section else ''}")

    # Build existing marks map
    existing_marks = {}
    if selected_exam and selected_class and students:
        marks_qs = ExamMark.objects.filter(
            exam=selected_exam,
            class_level=selected_class,
            student__in=students,
        )
        for m in marks_qs:
            existing_marks[(m.student_id, m.subject_id)] = m

    grand_total_max = sum(cs.total_marks for cs in class_subjects)

    for idx, s in enumerate(students, start=1):
        subj_inputs = []
        row_total = Decimal("0.0")
        has_any_mark = False

        for cs in class_subjects:
            m = existing_marks.get((s.id, cs.subject_id))
            if m:
                has_any_mark = True
                if m.is_absent:
                    score = "A"
                    is_abs = True
                else:
                    score = int(m.obtained_marks) if m.obtained_marks % 1 == 0 else m.obtained_marks
                    row_total += m.obtained_marks
                    is_abs = False
            else:
                score = ""
                is_abs = False

            subj_inputs.append({
                "class_subject": cs,
                "score": score,
                "is_absent": is_abs,
                "max_marks": int(cs.total_marks) if cs.total_marks % 1 == 0 else cs.total_marks,
            })

        student_grid_rows.append({
            "sr_no": idx,
            "student": s,
            "subjects": subj_inputs,
            "row_total": int(row_total) if row_total % 1 == 0 else row_total,
            "has_any_mark": has_any_mark,
        })

    context = {
        "school_setting": school_setting,
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "class_subjects": class_subjects,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
        "student_grid_rows": student_grid_rows,
        "total_students": len(students),
    }
    return render(request, "exams/class_marks_entry_grid.html", context)


# ==============================================================================
# BULK PRINT ALL RESULT CARDS / DMCS FOR A CLASS
# ==============================================================================

@login_required
def bulk_dmc_print(request):
    """
    Bulk Print Detailed Marks Certificates (DMC) for all students of a class at once.
    Each student gets a full-page report card with school logo, marks breakdown,
    percentages, rank, and signatures, separated by print page breaks.
    """
    school_setting = SchoolSetting.objects.first()
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = []
    grand_total_max = 0
    student_records = []
    stats = {}

    if selected_exam and selected_class:
        class_subjects, grand_total_max, student_records, stats = compute_class_result_matrix(
            selected_exam, selected_class, selected_section
        )

    context = {
        "school_setting": school_setting,
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "class_subjects": class_subjects,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
        "student_records": student_records,
        "stats": stats,
    }
    return render(request, "exams/bulk_student_dmc.html", context)


# ==============================================================================
# MULTI-SUBJECT CLASS TEMPLATE EXPORT & BULK IMPORT
# ==============================================================================

@login_required
def export_class_template_excel(request):
    """
    Exports a multi-subject blank/prefilled marks entry spreadsheet for teachers to fill via Excel/Google Sheets.
    """
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)
    section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = list(
        ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
    )
    if not class_subjects:
        seed_default_subjects_for_class(class_level)
        class_subjects = list(
            ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
        )

    students_qs = Student.objects.filter(current_class=class_level, status="Active").order_by("admission_no")
    if section:
        students_qs = students_qs.filter(current_section=section)

    existing_marks = {
        (m.student_id, m.subject_id): m
        for m in ExamMark.objects.filter(exam=exam, class_level=class_level)
    }

    wb = Workbook()
    ws = wb.active
    ws.title = f"MarksEntry_{class_level.name[:10]}"

    school_name = "KOHISAR MODEL SCHOOL & COLLEGE QALAGAY SWAT"
    sub_title = f"MULTI-SUBJECT MARKS ENTRY SHEET — CLASS {class_level.name.upper()} — {exam.name.upper()}"
    if section:
        sub_title += f" (SECTION {section.name})"

    total_cols = 4 + len(class_subjects)

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    ws["A1"] = school_name
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1A365D")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    ws["A2"] = sub_title
    ws["A2"].font = Font(name="Arial", size=11, bold=True, color="2B6CB0")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # Embed school logo if available
    logo_file = os.path.join(settings.BASE_DIR, "static", "dist", "img", "logo.png")
    if os.path.exists(logo_file):
        try:
            from openpyxl.drawing.image import Image as XLImage
            xl_img = XLImage(logo_file)
            xl_img.width = 46
            xl_img.height = 46
            ws.add_image(xl_img, "A1")
        except Exception:
            pass

    headers = ["Sr No", "Admission #", "Name", "Father's Name"]
    for cs in class_subjects:
        headers.append(cs.header_label)

    header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    border = get_thin_border()

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws.row_dimensions[3].height = 26

    data_font = Font(name="Arial", size=10)
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    entry_fill = PatternFill(start_color="FEFCBF", end_color="FEFCBF", fill_type="solid")

    for row_idx, s in enumerate(students_qs, start=4):
        sr = row_idx - 3
        is_alt = (row_idx % 2 == 0)
        row_vals = [sr, s.admission_no, s.full_name, s.father_name]

        for cs in class_subjects:
            m = existing_marks.get((s.id, cs.subject_id))
            if m:
                score_str = "A" if m.is_absent else (int(m.obtained_marks) if m.obtained_marks % 1 == 0 else float(m.obtained_marks))
            else:
                score_str = ""
            row_vals.append(score_str)

        for col_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = data_font
            cell.border = border

            if col_idx in [1, 2]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if is_alt:
                    cell.fill = alt_fill
            elif col_idx in [3, 4]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                if is_alt:
                    cell.fill = alt_fill
            else:
                # Subject entry cells: highlighted in pale yellow
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.font = Font(name="Arial", size=10, bold=True)
                cell.fill = entry_fill

        ws.row_dimensions[row_idx].height = 20

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 24
    for idx in range(5, 5 + len(class_subjects)):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = 13

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"Marks_Entry_{class_level.name}_{exam.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)


@login_required
def import_class_result_excel(request):
    """
    Imports a multi-subject class result Excel spreadsheet uploaded by teacher/admin.
    Automatically parses all dynamic subject columns and updates student marks.
    """
    if request.method != "POST":
        return redirect("class_marks_entry_grid")

    exam_id = request.POST.get("exam_id")
    class_id = request.POST.get("class_id")
    uploaded_file = request.FILES.get("excel_file")

    if not (exam_id and class_id and uploaded_file):
        messages.error(request, "Missing examination, class, or Excel file.")
        return redirect("class_marks_entry_grid")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)

    class_subjects = list(ClassSubject.objects.filter(class_level=class_level).select_related("subject"))

    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {str(e)}")
        return redirect(f"class_marks_entry_grid?exam_id={exam.id}&class_id={class_level.id}")

    # Locate header row (contains "admission" or "name" or subject names)
    header_idx = -1
    for idx, r in enumerate(rows[:10]):
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if "name" in row_str and ("adm" in row_str or "father" in row_str or "sr" in row_str):
            header_idx = idx
            break

    if header_idx == -1:
        messages.error(request, "Could not locate valid column headers in the uploaded Excel file.")
        return redirect(f"class_marks_entry_grid?exam_id={exam.id}&class_id={class_level.id}")

    raw_headers = [str(c).strip().lower() if c is not None else "" for c in rows[header_idx]]

    adm_col = -1
    name_col = -1
    fname_col = -1
    subject_col_map = {}  # col_idx -> ClassSubject

    for c_idx, h in enumerate(raw_headers):
        if "admission" in h or "adm" in h:
            adm_col = c_idx
        elif "father" in h or "f/name" in h or "f.name" in h:
            fname_col = c_idx
        elif "name" in h and "father" not in h and "f/name" not in h:
            name_col = c_idx
        else:
            # Check if this column matches any subject
            for cs in class_subjects:
                s_name = cs.subject.name.lower()
                s_code = cs.subject.short_name.lower()
                if s_code in h or s_name in h:
                    subject_col_map[c_idx] = cs
                    break

    class_students = Student.objects.filter(current_class=class_level)
    student_by_adm = {s.admission_no.strip().lower(): s for s in class_students if s.admission_no}
    student_by_name = {s.full_name.strip().lower(): s for s in class_students}

    updated_entries = 0
    updated_students = set()
    newly_added_students = 0

    with transaction.atomic():
        for r_idx, row_values in enumerate(rows[header_idx + 1:], start=header_idx + 2):
            if not any(row_values):
                continue

            target_student = None
            adm_val = str(row_values[adm_col]).strip() if adm_col != -1 and adm_col < len(row_values) and row_values[adm_col] else ""
            name_val = str(row_values[name_col]).strip() if name_col != -1 and name_col < len(row_values) and row_values[name_col] else ""
            fname_val = str(row_values[fname_col]).strip() if fname_col != -1 and fname_col < len(row_values) and row_values[fname_col] else ""

            if adm_val:
                target_student = student_by_adm.get(adm_val.lower())
                if not target_student:
                    # Check globally across school
                    target_student = Student.objects.filter(admission_no__iexact=adm_val).first()
                    if target_student and target_student.current_class != class_level:
                        target_student.current_class = class_level
                        target_student.save(update_fields=["current_class"])

            if not target_student and name_val:
                target_student = student_by_name.get(name_val.lower())
                if not target_student:
                    # Check globally by name
                    target_student = Student.objects.filter(full_name__iexact=name_val).first()
                    if target_student and target_student.current_class != class_level:
                        target_student.current_class = class_level
                        target_student.save(update_fields=["current_class"])

            # If student is new, auto-add to this class and to the result
            if not target_student and name_val:
                default_section = Section.objects.filter(class_level=class_level).first()
                target_student = Student(
                    full_name=name_val,
                    father_name=fname_val or "Guardian",
                    current_class=class_level,
                    current_section=default_section,
                    status="Active",
                )
                if adm_val and not Student.objects.filter(admission_no=adm_val).exists():
                    target_student.admission_no = adm_val
                target_student.save()
                student_by_adm[target_student.admission_no.lower()] = target_student
                student_by_name[target_student.full_name.lower()] = target_student
                newly_added_students += 1

            if not target_student:
                continue

            for col_idx, cs in subject_col_map.items():
                if col_idx < len(row_values):
                    val = row_values[col_idx]
                    if val is None or str(val).strip() == "":
                        continue

                    val_str = str(val).strip().upper()
                    if val_str in ["A", "ABS", "ABSENT"]:
                        ExamMark.objects.update_or_create(
                            exam=exam,
                            student=target_student,
                            subject=cs.subject,
                            defaults={
                                "class_level": class_level,
                                "total_marks": cs.total_marks,
                                "obtained_marks": Decimal("0.0"),
                                "is_absent": True,
                            }
                        )
                        updated_entries += 1
                        updated_students.add(target_student.id)
                    else:
                        try:
                            dec_val = Decimal(re.sub(r"[^\d.]", "", val_str))
                            dec_val = min(dec_val, cs.total_marks)
                            dec_val = max(dec_val, Decimal("0.0"))
                            ExamMark.objects.update_or_create(
                                exam=exam,
                                student=target_student,
                                subject=cs.subject,
                                defaults={
                                    "class_level": class_level,
                                    "total_marks": cs.total_marks,
                                    "obtained_marks": dec_val,
                                    "is_absent": False,
                                }
                            )
                            updated_entries += 1
                            updated_students.add(target_student.id)
                        except Exception:
                            continue

    new_info = f" (including {newly_added_students} newly added student(s) to {class_level.name})" if newly_added_students > 0 else ""
    messages.success(
        request,
        f"Import completed! Successfully processed {updated_entries} subject marks for {len(updated_students)} student(s) in {class_level.name}{new_info} with zero duplicates."
    )
    return redirect(f"/exams/class-result/?exam_id={exam.id}&class_id={class_level.id}")


# ==============================================================================
# ROLL NUMBER SLIPS & EXAMINATION ADMIT CARDS GENERATOR
# ==============================================================================

@login_required
def roll_number_slips(request):
    """
    Examination Roll Number Slips & Admit Cards Generator.
    Supports single class or Full School (All Classes) batch printing.
    Includes student bio, candidate photo / affix box, school logo,
    class subjects date sheet list, exam instructions, and signature lines.
    """
    school_setting = SchoolSetting.objects.first()
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id", "all")
    section_id = request.GET.get("section_id")
    student_query = request.GET.get("q", "").strip()
    student_id = request.GET.get("student_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()

    is_all_classes = (class_id == "all" or not class_id)
    selected_class = None
    if not is_all_classes:
        selected_class = ClassLevel.objects.filter(id=class_id).first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    # Query students
    students_qs = Student.objects.filter(status="Active").select_related("current_class", "current_section").order_by("current_class__name", "admission_no")

    if not is_all_classes and selected_class:
        students_qs = students_qs.filter(current_class=selected_class)
        if selected_section:
            students_qs = students_qs.filter(current_section=selected_section)

    if student_id:
        students_qs = students_qs.filter(id=student_id)

    if student_query:
        students_qs = students_qs.filter(
            Q(full_name__icontains=student_query) |
            Q(admission_no__icontains=student_query) |
            Q(father_name__icontains=student_query)
        )

    students = list(students_qs)

    # Pre-fetch ClassSubjects for relevant classes
    class_ids = set(s.current_class_id for s in students if s.current_class_id)
    all_class_subjects = ClassSubject.objects.filter(class_level_id__in=class_ids).select_related("subject").order_by("order", "subject__order")

    class_subjects_map = {}
    for cs in all_class_subjects:
        if cs.class_level_id not in class_subjects_map:
            class_subjects_map[cs.class_level_id] = []
        class_subjects_map[cs.class_level_id].append(cs)

    # Build slip records
    slip_records = []
    for idx, s in enumerate(students, start=1):
        c_subs = class_subjects_map.get(s.current_class_id, [])
        slip_records.append({
            "roll_no": s.admission_no,
            "student": s,
            "class_level": s.current_class,
            "section": s.current_section,
            "subjects": c_subs,
        })

    context = {
        "school_setting": school_setting,
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "is_all_classes": is_all_classes,
        "class_id": class_id,
        "student_query": student_query,
        "slip_records": slip_records,
        "total_slips": len(slip_records),
    }
    return render(request, "exams/roll_number_slips.html", context)


@login_required
def single_student_roll_number_slip(request, student_id, exam_id=None):
    """
    Individual Candidate Examination Roll Number Slip / Admit Card.
    Allows printing a single student's roll number slip directly.
    """
    student = get_object_or_404(Student, id=student_id)
    school_setting = SchoolSetting.objects.first()
    exams = Exam.objects.all().order_by("-start_date", "-id")

    req_exam_id = request.GET.get("exam_id") or exam_id
    selected_exam = None
    if req_exam_id:
        selected_exam = Exam.objects.filter(id=req_exam_id).first()
    if not selected_exam:
        selected_exam = exams.filter(is_active=True).first() or exams.first()

    # Get class subjects for the candidate's class
    subjects = []
    if student.current_class:
        subjects = ClassSubject.objects.filter(
            class_level=student.current_class
        ).select_related("subject").order_by("order", "subject__order")

    slip = {
        "roll_no": student.admission_no,
        "student": student,
        "class_level": student.current_class,
        "section": student.current_section,
        "subjects": subjects,
    }

    context = {
        "school_setting": school_setting,
        "student": student,
        "selected_exam": selected_exam,
        "exams": exams,
        "slip": slip,
    }
    return render(request, "exams/single_roll_number_slip.html", context)


# ==============================================================================
# BLANK MARKS COLLECTION SHEET (FOR TEACHERS TO HANDWRITE / DISTRIBUTE)
# ==============================================================================

@login_required
def blank_marks_sheet(request):
    """
    Renders a completely blank student marks collection sheet for each class with all subjects.
    Cells are completely empty (no dashes, no text) so teachers can easily handwrite marks
    or use it as a physical award list.
    """
    school_setting = SchoolSetting.objects.first()
    exams = Exam.objects.all().order_by("-start_date", "-id")
    classes = ClassLevel.objects.all().order_by("name")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    # Get class subjects
    class_subjects = []
    grand_total_max = 0
    if selected_class:
        class_subjects = list(
            ClassSubject.objects.filter(class_level=selected_class)
            .select_related("subject")
            .order_by("order", "subject__order")
        )
        if not class_subjects:
            seed_default_subjects_for_class(selected_class)
            class_subjects = list(
                ClassSubject.objects.filter(class_level=selected_class)
                .select_related("subject")
                .order_by("order", "subject__order")
            )
        grand_total_max = sum(cs.total_marks for cs in class_subjects)

    # Students query
    students_qs = Student.objects.filter(
        current_class=selected_class, status="Active"
    ).select_related("current_section").order_by("admission_no", "full_name")

    if selected_section:
        students_qs = students_qs.filter(current_section=selected_section)

    students = list(students_qs)

    context = {
        "school_setting": school_setting,
        "exams": exams,
        "classes": classes,
        "sections": sections,
        "selected_exam": selected_exam,
        "selected_class": selected_class,
        "selected_section": selected_section,
        "class_subjects": class_subjects,
        "grand_total_max": int(grand_total_max) if grand_total_max % 1 == 0 else grand_total_max,
        "students": students,
        "total_students": len(students),
    }
    return render(request, "exams/blank_marks_sheet.html", context)


@login_required
def export_blank_marks_excel(request):
    """
    Exports a completely blank multi-subject Excel spreadsheet for a class.
    Cells are clean and blank for handwriting or digital input.
    """
    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id")
    section_id = request.GET.get("section_id")

    exam = get_object_or_404(Exam, id=exam_id) if exam_id else Exam.objects.filter(is_active=True).first() or Exam.objects.first()
    class_level = get_object_or_404(ClassLevel, id=class_id) if class_id else ClassLevel.objects.first()
    section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = list(
        ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
    )
    if not class_subjects:
        seed_default_subjects_for_class(class_level)
        class_subjects = list(
            ClassSubject.objects.filter(class_level=class_level).select_related("subject").order_by("order", "subject__order")
        )

    students_qs = Student.objects.filter(current_class=class_level, status="Active").order_by("admission_no", "full_name")
    if section:
        students_qs = students_qs.filter(current_section=section)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Blank_{class_level.name}"[:28]
    ws.views.sheetView[0].showGridLines = True

    # Title header
    total_cols = 4 + len(class_subjects) + 2  # S#, Roll, Name, Father, Subjects..., Total, Teacher Sign
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    title_cell = ws.cell(
        row=1, column=1,
        value="KOHISAR MODEL SCHOOL & COLLEGE — BLANK MARKS COLLECTION SHEET"
    )
    title_cell.font = Font(name="Arial", size=13, bold=True, color="1A365D")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 25

    # Subtitle
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    sub_cell = ws.cell(
        row=2, column=1,
        value=f"Class: {class_level.name} | Section: {section.name if section else 'All'} | Examination: {exam.name if exam else 'Term Exam'} | Session: {exam.session.name if exam and exam.session else 'Current'}"
    )
    sub_cell.font = Font(name="Arial", size=10, italic=True, color="4A5568")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # Headers
    headers = ["S#", "Roll / Adm #", "Student Name", "Father's Name"]
    for cs in class_subjects:
        headers.append(cs.header_label)
    headers.extend(["Obtained Total", "Teacher Sign"])

    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    border = get_thin_border()

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws.row_dimensions[3].height = 28

    data_font = Font(name="Arial", size=10)

    for row_idx, s in enumerate(students_qs, start=4):
        sr = row_idx - 3
        # Student info
        ws.cell(row=row_idx, column=1, value=sr).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=2, value=s.admission_no).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=3, value=s.full_name).alignment = Alignment(horizontal="left", vertical="center")
        ws.cell(row=row_idx, column=4, value=s.father_name).alignment = Alignment(horizontal="left", vertical="center")

        # Blank subject cells (empty string so no dashes, with border and tall height)
        for col_idx in range(5, 5 + len(class_subjects) + 2):
            c = ws.cell(row=row_idx, column=col_idx, value="")
            c.alignment = Alignment(horizontal="center", vertical="center")

        for col_idx in range(1, total_cols + 1):
            ws.cell(row=row_idx, column=col_idx).font = data_font
            ws.cell(row=row_idx, column=col_idx).border = border

        # Comfortable height for writing
        ws.row_dimensions[row_idx].height = 24

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 22
    for idx in range(5, 5 + len(class_subjects)):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = 13
    ws.column_dimensions[get_column_letter(5 + len(class_subjects))].width = 14
    ws.column_dimensions[get_column_letter(6 + len(class_subjects))].width = 15

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"Blank_Marks_Sheet_{class_level.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)




