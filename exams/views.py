import io
import os
import re
from datetime import date, datetime
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

from finance.models import StudentFeeLedger
from finance.utils import initialize_ledger_months
from school.excel_utils import clean_adm_no, excel_download_response, get_thin_border, resolve_class_level
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
    classes = ClassLevel.objects.all().order_by("id")
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
    classes = ClassLevel.objects.all().order_by("id")
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
    classes = ClassLevel.objects.all().order_by("id")

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


def detect_class_mismatch(rows, uploaded_file, target_class):
    """
    Checks if an uploaded Excel file explicitly belongs to a DIFFERENT class than target_class.
    Prevents teachers from accidentally uploading e.g. a Class 4 spreadsheet into Class 3.
    """
    filename_lower = uploaded_file.name.lower()
    title_text = " ".join([str(c).lower() for r in rows[:4] for c in r if c is not None])

    target_clean = re.sub(r"[^a-z0-9]+", " ", target_class.name.lower()).strip()
    target_in_text = bool(re.search(r"\b" + re.escape(target_clean) + r"\b", title_text))
    target_in_file = bool(re.search(r"\b" + re.escape(target_clean.replace(" ", "_")) + r"\b", filename_lower)) or bool(re.search(r"\b" + re.escape(target_clean) + r"\b", filename_lower))

    if target_in_text or target_in_file:
        return None

    for other_c in ClassLevel.objects.exclude(id=target_class.id):
        other_clean = re.sub(r"[^a-z0-9]+", " ", other_c.name.lower()).strip()
        found_in_text = bool(re.search(r"\b" + re.escape(other_clean) + r"\b", title_text))
        found_in_file = bool(re.search(r"\b" + re.escape(other_clean.replace(" ", "_")) + r"\b", filename_lower)) or bool(re.search(r"\b" + re.escape(other_clean) + r"\b", filename_lower))
        if found_in_text or found_in_file:
            return other_c

    return None


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

    target_redirect = f"/exams/award-sheet/?exam_id={exam.id}&class_id={class_level.id}&subject_id={subject.id}"

    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {str(e)}")
        return redirect(target_redirect)

    # Validate against class mismatch
    mismatched_class = detect_class_mismatch(rows, uploaded_file, class_level)
    if mismatched_class:
        messages.error(
            request,
            f"Class Mismatch Warning! The uploaded file appears to be for '{mismatched_class.name}', "
            f"but you currently have '{class_level.name}' selected. "
            f"Upload was stopped to prevent corrupting student data."
        )
        return redirect(target_redirect)

    # Find header row (contains "name" or "o/marks" or "admission")
    header_idx = -1
    for idx, r in enumerate(rows[:10]):
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if "name" in row_str and ("marks" in row_str or "o/marks" in row_str or "s#no" in row_str):
            header_idx = idx
            break

    if header_idx == -1:
        messages.error(request, "Could not find valid column headers in the uploaded Excel file.")
        return redirect(target_redirect)

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
    class_students = list(Student.objects.filter(current_class=class_level))
    student_by_adm = {clean_adm_no(s.admission_no).lower(): s for s in class_students if s.admission_no}

    updated_count = 0
    newly_added = 0
    skipped_count = 0
    errors = []

    try:
        with transaction.atomic():
            for r_idx, row_values in enumerate(rows[header_idx + 1:], start=header_idx + 2):
                if not any(row_values):
                    continue

                target_student = None
                adm_val = clean_adm_no(row_values[adm_col]) if adm_col != -1 and adm_col < len(row_values) and row_values[adm_col] is not None else ""
                name_val = str(row_values[name_col]).strip() if name_col != -1 and name_col < len(row_values) and row_values[name_col] is not None else ""
                fname_val = str(row_values[fname_col]).strip() if fname_col != -1 and fname_col < len(row_values) and row_values[fname_col] is not None else ""

                # 1. Match by admission number within THIS class
                if adm_val:
                    target_student = student_by_adm.get(adm_val.lower())

                # 2. If not matched by admission number, match by name+father ONLY if no conflicting admission number
                if not target_student and name_val:
                    for s in class_students:
                        if s.full_name.strip().lower() == name_val.lower():
                            father_matches = (
                                not fname_val or not s.father_name or
                                s.father_name.strip().lower() == fname_val.lower()
                            )
                            s_adm = clean_adm_no(s.admission_no).lower() if s.admission_no else ""
                            if father_matches and (not s_adm or not adm_val or s_adm == adm_val.lower()):
                                target_student = s
                                if adm_val and not s.admission_no:
                                    target_student.admission_no = adm_val
                                    target_student.save(update_fields=["admission_no"])
                                    student_by_adm[adm_val.lower()] = target_student
                                break

                # 3. If student is brand new, auto-add to THIS class and to the result
                if not target_student and name_val:
                    default_section = Section.objects.filter(class_level=class_level).first()
                    if not default_section:
                        default_section = Section.objects.create(class_level=class_level, name="A")
                    target_student = Student(
                        full_name=name_val,
                        father_name=fname_val,
                        admission_no=adm_val,
                        current_class=class_level,
                        current_section=default_section,
                        status="Active",
                        dob=date(2015, 1, 1),
                        gender="Male",
                        admission_date=timezone.now().date(),
                        residence="",
                        contact_number="",
                    )
                    target_student.save()
                    class_students.append(target_student)
                    if adm_val:
                        student_by_adm[adm_val.lower()] = target_student
                    newly_added += 1

                # If student matched and father name was not known, update if provided now
                if target_student and fname_val and (not target_student.father_name or target_student.father_name.strip().lower() in ["guardian", "", "-", "none", "not provided"]):
                    target_student.father_name = fname_val
                    target_student.save(update_fields=["father_name"])

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
                    except Exception:
                        errors.append(f"Row {r_idx}: Invalid marks '{obt_raw}' for {target_student.full_name}")

        new_info = f" ({newly_added} newly enrolled)" if newly_added > 0 else ""
        if updated_count > 0:
            messages.success(request, f"Successfully imported marks for {updated_count} student(s) in {subject.name}{new_info}!")
        if skipped_count > 0:
            messages.info(request, f"{skipped_count} row(s) were skipped (blank or unmatched).")
        if errors:
            messages.warning(request, f"Some rows had issues: {'; '.join(errors[:3])}")
    except Exception as e:
        messages.error(request, f"Excel Import Failed: {str(e)}")

    return redirect(f"/exams/award-sheet/?exam_id={exam.id}&class_id={class_level.id}&subject_id={subject.id}")


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
    school_setting = SchoolSetting.objects.first()
    pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0
    pass_rule = school_setting.passing_rule if (school_setting and school_setting.passing_rule) else "overall_only"

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
    def natural_adm_sort_key(s):
        adm = clean_adm_no(s.admission_no)
        try:
            return (0, int(adm))
        except (ValueError, TypeError):
            return (1, adm.lower())

    students_qs = Student.objects.filter(current_class=class_level, status="Active")
    if section:
        students_qs = students_qs.filter(current_section=section)
    students = sorted(list(students_qs), key=natural_adm_sort_key)

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

        # Calculate percentage, grade, and status based on school passing criteria
        if grand_total_max > 0 and not all_absent and has_any_mark:
            percentage = round((float(obtained_total) / float(grand_total_max)) * 100, 2)
            grade = calculate_grade(percentage, passing_pct=pass_pct)
            if pass_rule == "overall_only":
                status = "Pass" if percentage >= pass_pct else "Fail"
            elif pass_rule == "subject_only":
                status = "Fail" if has_failed_subject else "Pass"
            else:  # subject_and_overall
                status = "Fail" if (has_failed_subject or percentage < pass_pct) else "Pass"
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

    # Put back in natural admission_no order for display
    student_records.sort(key=lambda x: natural_adm_sort_key(x["student"]))
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
        "criteria_pass_pct": pass_pct,
        "criteria_pass_rule": pass_rule,
    }

    return class_subjects, grand_total_max, student_records, stats


@login_required
def class_result_sheet(request):
    """
    Master Class Result Sheet (Image 1 format).
    Displays multi-subject results, Grand Total, %age, Position, and Grade.
    """
    exams = Exam.objects.all()
    classes = ClassLevel.objects.all().order_by("id")

    exam_id = request.GET.get("exam_id")
    class_id = request.GET.get("class_id") or request.session.get("last_grid_class_id")
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
    classes = ClassLevel.objects.all().order_by("id")

    exam_id = request.GET.get("exam_id") or request.POST.get("exam_id")
    class_id = request.GET.get("class_id") or request.POST.get("class_id") or request.session.get("last_grid_class_id")
    section_id = request.GET.get("section_id") or request.POST.get("section_id")

    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()
    selected_class = ClassLevel.objects.filter(id=class_id).first() if class_id else classes.first()

    if selected_class:
        request.session["last_grid_class_id"] = selected_class.id

    sections = Section.objects.filter(class_level=selected_class) if selected_class else []
    selected_section = Section.objects.filter(id=section_id).first() if section_id else None

    class_subjects = []
    students = []
    student_grid_rows = []

    def natural_adm_sort_key(s):
        adm = clean_adm_no(s.admission_no)
        try:
            return (0, int(adm))
        except (ValueError, TypeError):
            return (1, adm.lower())

    if selected_class:
        class_subjects = list(
            ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order", "subject__order")
        )
        if not class_subjects:
            seed_default_subjects_for_class(selected_class)
            class_subjects = list(
                ClassSubject.objects.filter(class_level=selected_class).select_related("subject").order_by("order", "subject__order")
            )

        students_qs = Student.objects.filter(current_class=selected_class, status="Active")
        if selected_section:
            students_qs = students_qs.filter(current_section=selected_section)
        students = sorted(list(students_qs), key=natural_adm_sort_key)

    # Handle Quick-Add Student directly to this class
    if request.method == "POST" and request.POST.get("action") == "quick_add_student":
        q_name = request.POST.get("full_name", "").strip()
        q_fname = request.POST.get("father_name", "").strip()
        q_adm = clean_adm_no(request.POST.get("admission_no", ""))
        q_sec_id = request.POST.get("section_id")
        q_gender = request.POST.get("gender", "Male").strip().capitalize()
        if q_gender not in ["Male", "Female"]:
            q_gender = "Male"

        sec_obj = Section.objects.filter(id=q_sec_id, class_level=selected_class).first() if q_sec_id else None
        if not sec_obj and selected_class:
            sec_obj = Section.objects.filter(class_level=selected_class).first()
            if not sec_obj:
                sec_obj = Section.objects.create(class_level=selected_class, name="A")

        if not q_name:
            messages.error(request, "Student Full Name is required.")
        else:
            if q_adm and Student.objects.filter(current_class=selected_class, admission_no__iexact=q_adm).exists():
                existing = Student.objects.filter(current_class=selected_class, admission_no__iexact=q_adm).first()
                messages.error(request, f"Admission # '{q_adm}' is already used by '{existing.full_name}' in this class. Please choose a unique number for {selected_class.name}.")
            else:
                new_s = Student(
                    full_name=q_name,
                    father_name=q_fname,
                    gender=q_gender,
                    current_class=selected_class,
                    current_section=sec_obj,
                    status="Active",
                    admission_date=timezone.now().date(),
                    dob=date(2015, 1, 1),
                )
                if q_adm:
                    new_s.admission_no = q_adm
                new_s.save()

                active_session = AcademicSession.objects.filter(is_active=True).first()
                if active_session and selected_class:
                    try:
                        ledger, _ = StudentFeeLedger.objects.get_or_create(
                            student=new_s,
                            academic_session=active_session,
                        )
                        initialize_ledger_months(ledger, new_s, selected_class.monthly_fee)
                    except Exception:
                        pass

                messages.success(request, f"Student '{q_name}' (Adm # {new_s.admission_no}) added directly to {selected_class.name}!")

        return redirect(f"{request.path}?exam_id={selected_exam.id}&class_id={selected_class.id}&section_id={selected_section.id if selected_section else ''}")

    # Handle POST - Save Grid Marks & Admission Numbers directly from web
    if request.method == "POST" and request.POST.get("action") == "save_grid_marks":
        saved_marks_count = 0
        updated_adm_count = 0
        with transaction.atomic():
            for s in students:
                # Update admission number if changed in the grid
                adm_key = f"adm_{s.id}"
                if adm_key in request.POST:
                    new_adm = clean_adm_no(request.POST.get(adm_key, ""))
                    if new_adm != s.admission_no:
                        s.admission_no = new_adm
                        s.save(update_fields=["admission_no"])
                        updated_adm_count += 1

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

        adm_info = f" and updated {updated_adm_count} admission #s" if updated_adm_count > 0 else ""
        messages.success(request, f"Successfully saved {saved_marks_count} marks entries{adm_info} for {len(students)} students in {selected_class.name}!")
        return redirect(f"{request.path}?exam_id={selected_exam.id}&class_id={selected_class.id}&section_id={selected_section.id if selected_section else ''}")

    # Handle POST - Save Passing Criteria as School Default
    if request.method == "POST" and request.POST.get("action") == "save_passing_criteria":
        new_pct = request.POST.get("passing_percentage")
        new_rule = request.POST.get("passing_rule", "overall_only")
        if new_pct:
            try:
                setting_obj = SchoolSetting.objects.first()
                if not setting_obj:
                    setting_obj = SchoolSetting.objects.create()
                setting_obj.passing_percentage = Decimal(str(new_pct).strip())
                setting_obj.passing_rule = new_rule
                setting_obj.save()
                messages.success(request, f"Passing criteria updated to {setting_obj.passing_percentage}% ({setting_obj.get_passing_rule_display()}) and saved as school default!")
            except Exception as e:
                messages.error(request, f"Could not update passing criteria: {e}")
        return redirect(f"{request.path}?exam_id={selected_exam.id if selected_exam else ''}&class_id={selected_class.id if selected_class else ''}&section_id={selected_section.id if selected_section else ''}")

    # Handle POST - Sync Class Subject Passing Marks
    if request.method == "POST" and request.POST.get("action") == "sync_class_subject_pass_marks":
        pct_raw = request.POST.get("passing_percentage") or (school_setting.passing_percentage if school_setting else 30.0)
        try:
            pct_val = Decimal(str(pct_raw).strip())
            if selected_class:
                updated_count = 0
                for cs in ClassSubject.objects.filter(class_level=selected_class):
                    cs.passing_marks = round((cs.total_marks * pct_val) / Decimal("100.0"), 1)
                    cs.save()
                    updated_count += 1
                messages.success(request, f"Updated passing marks for {updated_count} subjects in {selected_class.name} to match {pct_val}% threshold.")
        except Exception as e:
            messages.error(request, f"Could not update subject passing marks: {e}")
        return redirect(f"{request.path}?exam_id={selected_exam.id if selected_exam else ''}&class_id={selected_class.id if selected_class else ''}&section_id={selected_section.id if selected_section else ''}")

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
    active_pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0
    active_pass_rule = school_setting.passing_rule if (school_setting and school_setting.passing_rule) else "overall_only"

    for idx, s in enumerate(students, start=1):
        subj_inputs = []
        row_total = Decimal("0.0")
        has_any_mark = False
        has_sub_fail = False

        for cs in class_subjects:
            m = existing_marks.get((s.id, cs.subject_id))
            if m:
                has_any_mark = True
                if m.is_absent:
                    score = "A"
                    is_abs = True
                    has_sub_fail = True
                else:
                    score = int(m.obtained_marks) if m.obtained_marks % 1 == 0 else m.obtained_marks
                    row_total += m.obtained_marks
                    is_abs = False
                    if m.obtained_marks < cs.passing_marks:
                        has_sub_fail = True
            else:
                score = ""
                is_abs = False

            subj_inputs.append({
                "class_subject": cs,
                "score": score,
                "is_absent": is_abs,
                "max_marks": int(cs.total_marks) if cs.total_marks % 1 == 0 else cs.total_marks,
                "passing_marks": int(cs.passing_marks) if cs.passing_marks % 1 == 0 else cs.passing_marks,
            })

        row_pct = round((float(row_total) / float(grand_total_max)) * 100, 1) if (grand_total_max > 0 and has_any_mark) else None
        row_grade = calculate_grade(row_pct, passing_pct=active_pass_pct) if row_pct is not None else "-"
        if row_pct is not None:
            if active_pass_rule == "overall_only":
                row_status = "Pass" if row_pct >= active_pass_pct else "Fail"
            elif active_pass_rule == "subject_only":
                row_status = "Fail" if has_sub_fail else "Pass"
            else:
                row_status = "Pass" if (not has_sub_fail and row_pct >= active_pass_pct) else "Fail"
        else:
            row_status = "-"

        student_grid_rows.append({
            "sr_no": idx,
            "student": s,
            "subjects": subj_inputs,
            "row_total": int(row_total) if row_total % 1 == 0 else row_total,
            "row_pct": row_pct,
            "row_grade": row_grade,
            "row_status": row_status,
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
        "passing_percentage": active_pass_pct,
        "passing_rule": active_pass_rule,
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
    classes = ClassLevel.objects.all().order_by("id")

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

    def natural_adm_sort_key(s):
        adm = clean_adm_no(s.admission_no)
        try:
            return (0, int(adm))
        except (ValueError, TypeError):
            return (1, adm.lower())

    students_qs = Student.objects.filter(current_class=class_level, status="Active")
    if section:
        students_qs = students_qs.filter(current_section=section)
    students_list = sorted(list(students_qs), key=natural_adm_sort_key)

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

    if students_list:
        for row_idx, s in enumerate(students_list, start=4):
            sr = row_idx - 3
            is_alt = (row_idx % 2 == 0)
            row_vals = [sr, clean_adm_no(s.admission_no), s.full_name, s.father_name]

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
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.font = Font(name="Arial", size=10, bold=True)
                    cell.fill = entry_fill

            ws.row_dimensions[row_idx].height = 20
    else:
        # Provide sample empty guide rows for newly set up class
        nums = re.findall(r"\b(10|[1-9])\b", class_level.name)
        base_serial = int(nums[0]) * 100 if nums else 100
        for row_idx in range(4, 9):
            sr = row_idx - 3
            is_alt = (row_idx % 2 == 0)
            suggested_adm = str(base_serial + sr)
            row_vals = [sr, suggested_adm, f"Sample Student {sr}", "Guardian Name"] + ["" for _ in class_subjects]

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
                    cell.alignment = Alignment(horizontal="center", vertical="center")
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
    Imports a multi-subject class result Excel spreadsheet uploaded by teacher/admin,
    OR a student roster list with Admission Numbers for that class.
    Preserves admission numbers (e.g. 800-series for Class 8, 900-series for Class 9),
    guarantees students belong ONLY to this class, and prevents duplicate records or cross-class pollution.
    """
    if request.method != "POST":
        return redirect("class_marks_entry_grid")

    exam_id = request.POST.get("exam_id")
    class_id = request.POST.get("class_id")
    uploaded_file = request.FILES.get("excel_file")

    default_redirect = f"/exams/enter-marks/?exam_id={exam_id}&class_id={class_id}" if (exam_id and class_id) else "/exams/enter-marks/"
    target_redirect = request.POST.get("next") or request.META.get("HTTP_REFERER") or default_redirect

    if not (exam_id and class_id and uploaded_file):
        messages.error(request, "Missing examination, class, or Excel file.")
        return redirect(target_redirect)

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)

    class_subjects = list(ClassSubject.objects.filter(class_level=class_level).select_related("subject"))
    if not class_subjects:
        seed_default_subjects_for_class(class_level)
        class_subjects = list(ClassSubject.objects.filter(class_level=class_level).select_related("subject"))

    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {str(e)}")
        return redirect(target_redirect)

    # Validate against class mismatch
    mismatched_class = detect_class_mismatch(rows, uploaded_file, class_level)
    if mismatched_class:
        messages.error(
            request,
            f"Class Mismatch Detected! The uploaded spreadsheet appears to be for '{mismatched_class.name}', "
            f"but you currently have '{class_level.name}' selected. "
            f"Upload was aborted to prevent putting students into the wrong class."
        )
        return redirect(target_redirect)

    # Locate header row: scan first 12 rows
    header_idx = -1
    for idx, r in enumerate(rows[:12]):
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if ("name" in row_str or "student" in row_str) and (
            "adm" in row_str or "father" in row_str or "sr" in row_str or "roll" in row_str or "reg" in row_str
        ):
            header_idx = idx
            break

    # If still not found, check if row has >= 3 non-empty string headers
    if header_idx == -1:
        for idx, r in enumerate(rows[:6]):
            non_empty = [str(c).strip() for c in r if c is not None and str(c).strip()]
            if len(non_empty) >= 3 and any("name" in x.lower() for x in non_empty):
                header_idx = idx
                break

    if header_idx == -1:
        messages.error(request, "Could not locate valid column headers (Student Name, Admission #, Father Name) in the uploaded Excel file.")
        return redirect(target_redirect)

    raw_headers = [str(c).strip().lower() if c is not None else "" for c in rows[header_idx]]

    adm_col = -1
    name_col = -1
    fname_col = -1
    subject_col_map = {}  # col_idx -> ClassSubject

    for c_idx, h in enumerate(raw_headers):
        clean_h = re.sub(r"[^a-z0-9]+", "_", h).strip("_")
        # Identify Admission / Roll column
        if any(term in clean_h for term in ["admission", "adm", "roll", "reg_no", "reg_num", "student_id", "std_id"]):
            if "father" not in clean_h:
                adm_col = c_idx
        # Identify Father name column
        elif any(term in clean_h for term in ["father", "f_name", "fname", "guardian"]):
            fname_col = c_idx
        # Identify Student Name column
        elif any(term in clean_h for term in ["name", "student", "candidate"]):
            if "father" not in clean_h and "school" not in clean_h and "subject" not in clean_h:
                name_col = c_idx
        else:
            # Check if this column matches any subject of this class
            for cs in class_subjects:
                s_name = cs.subject.name.lower()
                s_code = cs.subject.short_name.lower()
                if s_code == clean_h or s_name in clean_h or s_code in clean_h:
                    subject_col_map[c_idx] = cs
                    break

    # If name_col not found, try finding any column with 'name'
    if name_col == -1:
        for c_idx, h in enumerate(raw_headers):
            if "name" in h and "father" not in h:
                name_col = c_idx
                break

    if name_col == -1:
        messages.error(request, "Could not find a 'Student Name' column in the uploaded file.")
        return redirect(target_redirect)

    # Students belonging STRICTLY to THIS class
    class_students = list(Student.objects.filter(current_class=class_level))
    student_by_adm = {clean_adm_no(s.admission_no).lower(): s for s in class_students if s.admission_no}

    updated_entries = 0
    updated_students = set()
    newly_added_students = 0
    active_session = AcademicSession.objects.filter(is_active=True).first()

    default_section = Section.objects.filter(class_level=class_level).first()
    if not default_section:
        default_section = Section.objects.create(class_level=class_level, name="A")

    try:
        with transaction.atomic():
            for r_idx, row_values in enumerate(rows[header_idx + 1:], start=header_idx + 2):
                if not any(row_values):
                    continue

                adm_val = clean_adm_no(row_values[adm_col]) if adm_col != -1 and adm_col < len(row_values) and row_values[adm_col] is not None else ""
                name_val = str(row_values[name_col]).strip() if name_col != -1 and name_col < len(row_values) and row_values[name_col] is not None else ""
                fname_val = str(row_values[fname_col]).strip() if fname_col != -1 and fname_col < len(row_values) and row_values[fname_col] is not None else ""

                if not name_val and not adm_val:
                    continue

                # Match strictly within THIS class
                target_student = None

                # 1. Match by admission number within THIS class
                if adm_val:
                    target_student = student_by_adm.get(adm_val.lower())

                # 2. If not matched by admission number, match by name+father ONLY if no conflicting admission number
                if not target_student and name_val:
                    for s in class_students:
                        if s.full_name.strip().lower() == name_val.lower():
                            father_matches = (
                                not fname_val or not s.father_name or
                                s.father_name.strip().lower() == fname_val.lower()
                            )
                            s_adm = clean_adm_no(s.admission_no).lower() if s.admission_no else ""
                            if father_matches and (not s_adm or not adm_val or s_adm == adm_val.lower()):
                                target_student = s
                                if adm_val and not s.admission_no:
                                    target_student.admission_no = adm_val
                                    target_student.save(update_fields=["admission_no"])
                                    student_by_adm[adm_val.lower()] = target_student
                                break

                # 3. If student does not exist in this class, CREATE them exclusively in this class
                if not target_student and name_val:
                    target_student = Student(
                        full_name=name_val,
                        father_name=fname_val,  # Clean blank if father not known in advance!
                        admission_no=adm_val,  # Exact admission number from Excel, NO class suffix, NO cross-class clash!
                        current_class=class_level,
                        current_section=default_section,
                        status="Active",
                        dob=date(2015, 1, 1),
                        gender="Male",
                        admission_date=timezone.now().date(),
                        residence="",
                        contact_number="",
                    )
                    target_student.save()
                    class_students.append(target_student)
                    if adm_val:
                        student_by_adm[adm_val.lower()] = target_student
                    newly_added_students += 1

                    # Initialize Fee Ledger
                    if active_session:
                        try:
                            ledger, _ = StudentFeeLedger.objects.get_or_create(
                                student=target_student,
                                academic_session=active_session,
                            )
                            initialize_ledger_months(ledger, target_student, class_level.monthly_fee)
                        except Exception:
                            pass

                # If student matched and father name was empty or not set, update with real father name if provided now
                if target_student and fname_val and (not target_student.father_name or target_student.father_name.strip().lower() in ["guardian", "", "-", "none", "not provided"]):
                    target_student.father_name = fname_val
                    target_student.save(update_fields=["father_name"])

                if not target_student:
                    continue

                # Process subject marks if columns exist
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
                                },
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
                                    },
                                )
                                updated_entries += 1
                                updated_students.add(target_student.id)
                            except Exception:
                                continue

        if newly_added_students > 0 and updated_entries > 0:
            msg = f"Excel Upload Success! Enrolled {newly_added_students} student(s) exclusively into {class_level.name} and saved {updated_entries} subject marks with zero duplicates."
        elif newly_added_students > 0:
            msg = f"Excel Upload Success! Enrolled {newly_added_students} student(s) with their admission numbers exclusively into {class_level.name}. They appear immediately in the grid below."
        elif updated_entries > 0:
            msg = f"Excel Marks Saved! Updated {updated_entries} marks for {len(updated_students)} student(s) in {class_level.name}."
        else:
            msg = f"Excel file processed successfully for {class_level.name}."

        messages.success(request, msg)

    except Exception as e:
        messages.error(request, f"Excel Import Failed: {str(e)}")

    redirect_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or default_redirect
    return redirect(redirect_url)


@login_required
def class_marks_reset(request):
    """
    Clears marks or purges all students for a specific class in an examination.
    Provides a safe, one-click reset for teachers if wrong data was entered or imported.
    """
    if request.method != "POST":
        return redirect("class_marks_entry_grid")

    exam_id = request.POST.get("exam_id")
    class_id = request.POST.get("class_id")
    reset_mode = request.POST.get("reset_mode", "marks_only")
    target_redirect = request.POST.get("next") or f"/exams/enter-marks/?exam_id={exam_id}&class_id={class_id}"

    if not (exam_id and class_id):
        messages.error(request, "Missing examination or class selection.")
        return redirect("class_marks_entry_grid")

    exam = get_object_or_404(Exam, id=exam_id)
    class_level = get_object_or_404(ClassLevel, id=class_id)

    try:
        with transaction.atomic():
            if reset_mode == "all_students":
                qs = Student.objects.filter(current_class=class_level)
                count = qs.count()
                qs.delete()
                messages.success(
                    request,
                    f"Successfully deleted all {count} student(s) from {class_level.name}, along with their marks and records."
                )
            else:
                # Default: marks_only
                marks_qs = ExamMark.objects.filter(exam=exam, class_level=class_level)
                count = marks_qs.count()
                marks_qs.delete()
                messages.success(
                    request,
                    f"Successfully cleared all {count} exam mark(s) for {class_level.name} in '{exam.name}'. Students remain enrolled."
                )
    except Exception as e:
        messages.error(request, f"Error resetting class data: {str(e)}")

    return redirect(target_redirect)


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
    classes = ClassLevel.objects.all().order_by("id")

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
    classes = ClassLevel.objects.all().order_by("id")

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


# ==============================================================================
# 1. WING & ALL-CLASS FULL RESULT BOOK / PRINTABLE REGISTERS
# ==============================================================================

WING_MAP = {
    "all": {"label": "Entire School (All Classes)", "levels": None},
    "Primary": {"label": "Primary Wing (Classes 1 - 5)", "levels": ["Primary"]},
    "Middle": {"label": "Middle Wing (Classes 6 - 8)", "levels": ["Middle"]},
    "High": {"label": "High School Wing (Classes 9 - 10)", "levels": ["High"]},
    "Higher Secondary": {"label": "Higher Secondary / College Wing (11th & 12th)", "levels": ["Higher Secondary"]},
    "Prep": {"label": "Pre-Primary / Junior Wing (Nursery & Prep)", "levels": ["Prep", "KG"]},
}


def _get_wing_result_data(exam, selected_wing_key="all"):
    """
    Helper to compile multi-class result matrices, wing statistics,
    and top overall position holders across the wing or whole school.
    """
    school_setting = SchoolSetting.objects.first()
    pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0

    wing_info = WING_MAP.get(selected_wing_key, WING_MAP["all"])
    levels = wing_info["levels"]

    classes_qs = ClassLevel.objects.all().order_by("id")
    if levels:
        classes_qs = classes_qs.filter(level__in=levels)

    class_results = []
    all_appeared_students = []

    total_enrolled = 0
    total_appeared = 0
    total_passed = 0
    total_failed = 0
    grades_distribution = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "Fail": 0}

    for cl in classes_qs:
        subjs, g_total_max, st_records, stats = compute_class_result_matrix(exam, cl)
        if not st_records and not subjs:
            continue

        class_results.append({
            "class_level": cl,
            "class_subjects": subjs,
            "grand_total_max": g_total_max,
            "student_records": st_records,
            "stats": stats,
        })

        total_enrolled += stats.get("total_enrolled", 0)
        total_appeared += stats.get("appeared", 0)
        total_passed += stats.get("passed", 0)
        total_failed += stats.get("failed", 0)

        for g_k, g_v in stats.get("grades_count", {}).items():
            if g_k in grades_distribution:
                grades_distribution[g_k] += g_v

        for rec in st_records:
            if rec["has_any_mark"] and not rec["all_absent"] and rec["percentage"] is not None:
                all_appeared_students.append({
                    "student": rec["student"],
                    "class_level": cl,
                    "obtained_total": rec["obtained_total"],
                    "obtained_total_num": rec["obtained_total_num"],
                    "grand_total_max": g_total_max,
                    "percentage": rec["percentage"],
                    "grade": rec["grade"],
                    "status": rec["status"],
                    "class_position": rec["position_display"],
                })

    # Sort all appeared students across the wing by percentage descending
    all_appeared_students.sort(key=lambda x: (x["percentage"], x["obtained_total_num"]), reverse=True)

    # Assign wing-level rank (handling ties)
    current_rank = 1
    for idx, cand in enumerate(all_appeared_students):
        if idx > 0 and cand["percentage"] == all_appeared_students[idx - 1]["percentage"]:
            cand["wing_position"] = all_appeared_students[idx - 1]["wing_position"]
        else:
            cand["wing_position"] = idx + 1
        cand["wing_position_display"] = get_position_suffix(cand["wing_position"])

    wing_pass_percentage = round((total_passed / total_appeared * 100), 2) if total_appeared > 0 else 0.0

    overall_stats = {
        "total_classes": len(class_results),
        "total_enrolled": total_enrolled,
        "total_appeared": total_appeared,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "pass_percentage": wing_pass_percentage,
        "grades_distribution": grades_distribution,
        "grades_list": [{"grade": k, "count": v} for k, v in grades_distribution.items()],
    }

    # Top position holders (Top 3 and Top 10)
    top_3_position_holders = [s for s in all_appeared_students if s.get("wing_position", 999) <= 3]
    top_10_students = all_appeared_students[:10]

    return {
        "exam": exam,
        "selected_wing_key": selected_wing_key,
        "wing_label": wing_info["label"],
        "class_results": class_results,
        "overall_stats": overall_stats,
        "top_3_position_holders": top_3_position_holders,
        "top_10_students": top_10_students,
        "all_appeared_students": all_appeared_students,
        "school_setting": school_setting,
    }


@login_required
def wing_result_book(request):
    """
    Wing-wise and School-wide Full Master Result Register (Screen View).
    Supports viewing full results for Primary, Middle, High, Higher Sec, or All Classes.
    """
    exams = Exam.objects.all().order_by("-is_active", "-created_at")
    exam_id = request.GET.get("exam_id")
    selected_exam = Exam.objects.filter(id=exam_id).first() if exam_id else exams.filter(is_active=True).first() or exams.first()

    selected_wing = request.GET.get("wing", "all")
    if selected_wing not in WING_MAP:
        selected_wing = "all"

    data = _get_wing_result_data(selected_exam, selected_wing) if selected_exam else None

    context = {
        "exams": exams,
        "selected_exam": selected_exam,
        "selected_wing": selected_wing,
        "wing_options": [{"key": k, "label": v["label"]} for k, v in WING_MAP.items()],
        "data": data,
    }
    return render(request, "exams/wing_result_book.html", context)


@login_required
def print_wing_result_book(request):
    """
    Print-ready / PDF format for Wing-wise or All-Class Full Result Book with official signatures.
    """
    exam_id = request.GET.get("exam_id")
    selected_exam = get_object_or_404(Exam, pk=exam_id) if exam_id else Exam.objects.filter(is_active=True).first() or Exam.objects.first()

    selected_wing = request.GET.get("wing", "all")
    if selected_wing not in WING_MAP:
        selected_wing = "all"

    data = _get_wing_result_data(selected_exam, selected_wing)

    context = {
        "selected_exam": selected_exam,
        "selected_wing": selected_wing,
        "data": data,
        "print_date": timezone.now().date(),
    }
    return render(request, "exams/print_wing_result_book.html", context)


@login_required
def export_wing_result_book_excel(request):
    """
    Generates a professionally styled Master Excel Workbook for the selected Wing/School result book.
    """
    exam_id = request.GET.get("exam_id")
    selected_exam = get_object_or_404(Exam, pk=exam_id) if exam_id else Exam.objects.filter(is_active=True).first()
    selected_wing = request.GET.get("wing", "all")
    if selected_wing not in WING_MAP:
        selected_wing = "all"

    data = _get_wing_result_data(selected_exam, selected_wing)

    wb = Workbook()
    # Sheet 1: Summary & Honor Roll
    ws_sum = wb.active
    ws_sum.title = "Wing Summary & Honors"

    title_banner = f"{data['school_setting'].name if data['school_setting'] else 'KMS'} - {data['wing_label']} Result Book ({selected_exam.name})"
    ws_sum.merge_cells("A1:G1")
    c1 = ws_sum.cell(row=1, column=1, value=title_banner)
    c1.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    c1.fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    c1.alignment = Alignment(horizontal="center", vertical="center")
    ws_sum.row_dimensions[1].height = 36

    # Overall KPIs
    stats = data["overall_stats"]
    kpis = [
        ("Total Classes Included", stats["total_classes"]),
        ("Total Students Enrolled", stats["total_enrolled"]),
        ("Total Students Appeared", stats["total_appeared"]),
        ("Total Passed", stats["total_passed"]),
        ("Total Failed", stats["total_failed"]),
        ("Overall Wing Pass %", f"{stats['pass_percentage']}%"),
    ]
    for idx, (lbl, val) in enumerate(kpis, start=3):
        ws_sum.cell(row=idx, column=1, value=lbl).font = Font(bold=True)
        ws_sum.cell(row=idx, column=2, value=val)

    # Top Honor Roll
    start_r = 11
    ws_sum.cell(row=start_r, column=1, value="WING / SCHOOL TOP POSITION HOLDERS").font = Font(bold=True, size=12, color="1A365D")
    headers_top = ["Position", "Roll / Adm #", "Student Name", "Class", "Marks Obtained", "Percentage", "Grade"]
    for col_i, h in enumerate(headers_top, 1):
        cell = ws_sum.cell(row=start_r + 1, column=col_i, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
        cell.border = get_thin_border()

    for idx, cand in enumerate(data["top_10_students"], start=start_r + 2):
        row_vals = [
            cand.get("wing_position_display", ""),
            cand["student"].admission_no,
            cand["student"].full_name,
            cand["class_level"].name,
            f"{cand['obtained_total']} / {int(cand['grand_total_max'])}",
            f"{cand['percentage']}%",
            cand["grade"],
        ]
        for col_i, val in enumerate(row_vals, 1):
            c = ws_sum.cell(row=idx, column=col_i, value=val)
            c.border = get_thin_border()

    # Individual Class Sheets
    for cr in data["class_results"]:
        cl = cr["class_level"]
        sheet_title = re.sub(r'[\\/*?:\[\]]', '_', cl.name)[:30]
        ws_cl = wb.create_sheet(title=sheet_title)

        ws_cl.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cr["class_subjects"]) + 7)
        banner = ws_cl.cell(row=1, column=1, value=f"{cl.name} — {selected_exam.name} Result Sheet")
        banner.font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
        banner.fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
        banner.alignment = Alignment(horizontal="center", vertical="center")
        ws_cl.row_dimensions[1].height = 32

        headers = ["S#", "Adm #", "Student Name", "Father's Name"]
        for cs in cr["class_subjects"]:
            headers.append(cs.header_label)
        headers.extend(["Obtained", "Total", "%age", "Grade", "Pos", "Status"])

        for col_i, h in enumerate(headers, 1):
            cell = ws_cl.cell(row=2, column=col_i, value=h)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
            cell.border = get_thin_border()
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_i, rec in enumerate(cr["student_records"], start=3):
            s = rec["student"]
            row_data = [rec.get("sr_no", row_i - 2), s.admission_no, s.full_name, s.father_name]
            for sm in rec["subject_marks"]:
                row_data.append(sm["score_display"])
            row_data.extend([
                rec["obtained_total"],
                int(cr["grand_total_max"]),
                f"{rec['percentage']}%" if rec["percentage"] is not None else "",
                rec["grade"],
                rec["position_display"],
                rec["status"],
            ])
            for col_i, val in enumerate(row_data, 1):
                c = ws_cl.cell(row=row_i, column=col_i, value=val)
                c.border = get_thin_border()
                c.alignment = Alignment(horizontal="center" if col_i not in (3, 4) else "left", vertical="center")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"Result_Book_{selected_wing}_{selected_exam.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)


# ==============================================================================
# 2. CONSOLIDATED ANNUAL RESULT (ALL TERMS CUMULATIVE & POSITION HOLDERS)
# ==============================================================================

def _get_consolidated_annual_data(session, selected_wing_key="all", selected_class_id=None):
    """
    Computes cumulative performance across all terms in an academic session:
    - Term 1, Mid Term, Final Term marks
    - Cumulative Grand Total, Overall %, Overall Grade, Final Status
    - Multi-Level Position Holders:
        1. School-Level Top Positions (1st, 2nd, 3rd) across the whole institution
        2. Wing-Level Top Positions (1st, 2nd, 3rd in Primary, Middle, High, Higher Sec)
        3. Class-Level Top Positions (1st, 2nd, 3rd in each class)
    - Full School-Wide Analytics & Grade Distribution
    """
    school_setting = SchoolSetting.objects.first()
    pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0

    # Exams in this session, ordered chronologically
    exams = list(Exam.objects.filter(session=session).order_by("created_at", "id"))

    wing_info = WING_MAP.get(selected_wing_key, WING_MAP["all"])
    levels = wing_info["levels"]

    classes_qs = ClassLevel.objects.all().order_by("id")
    if levels:
        classes_qs = classes_qs.filter(level__in=levels)
    if selected_class_id:
        classes_qs = classes_qs.filter(id=selected_class_id)

    # Pre-cache all ExamMark objects for this session
    marks_qs = ExamMark.objects.filter(
        exam__in=exams,
        class_level__in=classes_qs,
    ).select_related("exam", "student", "class_level", "subject")

    # (student_id, exam_id) -> list of ExamMark
    student_exam_marks = {}
    for m in marks_qs:
        student_exam_marks.setdefault((m.student_id, m.exam_id), []).append(m)

    # Pre-cache ClassSubject max marks per (class_id, exam_id or general)
    class_subjects_qs = ClassSubject.objects.filter(class_level__in=classes_qs)
    class_total_max = {}
    for cs in class_subjects_qs:
        class_total_max[cs.class_level_id] = class_total_max.get(cs.class_level_id, Decimal("0.0")) + cs.total_marks

    class_cumulative_rows = []
    all_school_candidates = []
    wing_candidates_map = {}  # wing_level -> list of candidates

    total_enrolled = 0
    total_appeared = 0
    total_passed = 0
    total_failed = 0
    school_grades_count = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "Fail": 0}

    for cl in classes_qs:
        students = list(Student.objects.filter(current_class=cl, status="Active").order_by("admission_no"))
        if not students:
            continue

        c_max_per_exam = float(class_total_max.get(cl.id, Decimal("100.0")))
        student_records = []

        for s in students:
            term_details = []
            cum_obtained = 0.0
            cum_max = 0.0
            terms_appeared_count = 0
            has_failed_any_term = False

            for exam in exams:
                m_list = student_exam_marks.get((s.id, exam.id), [])
                if m_list:
                    terms_appeared_count += 1
                    t_obtained = sum(float(m.obtained_marks) for m in m_list if not m.is_absent)
                    t_max = sum(float(m.total_marks) for m in m_list)
                    if t_max <= 0:
                        t_max = c_max_per_exam
                    t_pct = round((t_obtained / t_max * 100), 1) if t_max > 0 else 0.0
                    t_grade = calculate_grade(t_pct, passing_pct=pass_pct)
                    t_status = "Pass" if t_pct >= pass_pct else "Fail"
                    if t_status == "Fail":
                        has_failed_any_term = True

                    cum_obtained += t_obtained
                    cum_max += t_max
                    term_details.append({
                        "exam": exam,
                        "obtained": t_obtained,
                        "total_max": t_max,
                        "percentage": t_pct,
                        "grade": t_grade,
                        "status": t_status,
                        "appeared": True,
                    })
                else:
                    term_details.append({
                        "exam": exam,
                        "obtained": 0.0,
                        "total_max": c_max_per_exam,
                        "percentage": 0.0,
                        "grade": "-",
                        "status": "Pending",
                        "appeared": False,
                    })

            has_any_appearance = (terms_appeared_count > 0)
            cum_pct = round((cum_obtained / cum_max * 100), 2) if cum_max > 0 else 0.0
            cum_grade = calculate_grade(cum_pct, passing_pct=pass_pct) if has_any_appearance else "-"
            final_status = ("Pass" if cum_pct >= pass_pct else "Fail") if has_any_appearance else "Pending"

            rec = {
                "student": s,
                "class_level": cl,
                "term_details": term_details,
                "terms_appeared_count": terms_appeared_count,
                "cum_obtained": cum_obtained,
                "cum_max": cum_max,
                "cum_percentage": cum_pct,
                "cum_grade": cum_grade,
                "final_status": final_status,
                "has_any_appearance": has_any_appearance,
                "class_position": None,
                "class_position_display": "",
            }
            student_records.append(rec)

        # 1. Compute Class-Level Position Holders
        appeared_in_class = [r for r in student_records if r["has_any_appearance"]]
        appeared_in_class.sort(key=lambda x: (x["cum_percentage"], x["cum_obtained"]), reverse=True)
        for idx, r in enumerate(appeared_in_class):
            if idx > 0 and r["cum_percentage"] == appeared_in_class[idx - 1]["cum_percentage"]:
                r["class_position"] = appeared_in_class[idx - 1]["class_position"]
            else:
                r["class_position"] = idx + 1
            r["class_position_display"] = get_position_suffix(r["class_position"])

        # Class statistics
        cl_enrolled = len(students)
        cl_appeared = len(appeared_in_class)
        cl_passed = len([r for r in appeared_in_class if r["final_status"] == "Pass"])
        cl_failed = len([r for r in appeared_in_class if r["final_status"] == "Fail"])
        cl_pass_pct = round((cl_passed / cl_appeared * 100), 2) if cl_appeared > 0 else 0.0

        total_enrolled += cl_enrolled
        total_appeared += cl_appeared
        total_passed += cl_passed
        total_failed += cl_failed

        for r in appeared_in_class:
            g = r["cum_grade"]
            if g in school_grades_count:
                school_grades_count[g] += 1
            all_school_candidates.append(r)
            wing_candidates_map.setdefault(cl.level, []).append(r)

        class_cumulative_rows.append({
            "class_level": cl,
            "student_records": student_records,
            "enrolled": cl_enrolled,
            "appeared": cl_appeared,
            "passed": cl_passed,
            "failed": cl_failed,
            "pass_percentage": cl_pass_pct,
            "top_3_class": appeared_in_class[:3],
        })

    # 2. Compute School-Level Top Positions (1st, 2nd, 3rd) across the whole school
    all_school_candidates.sort(key=lambda x: (x["cum_percentage"], x["cum_obtained"]), reverse=True)
    for idx, cand in enumerate(all_school_candidates):
        if idx > 0 and cand["cum_percentage"] == all_school_candidates[idx - 1]["cum_percentage"]:
            cand["school_position"] = all_school_candidates[idx - 1]["school_position"]
        else:
            cand["school_position"] = idx + 1
        cand["school_position_display"] = get_position_suffix(cand["school_position"])

    school_top_position_holders = [c for c in all_school_candidates if c.get("school_position", 999) <= 3]
    school_top_10 = all_school_candidates[:10]

    # 3. Compute Wing-Level Top Positions for each wing category
    wing_top_positions = {}
    for w_lvl, w_cands in wing_candidates_map.items():
        w_cands.sort(key=lambda x: (x["cum_percentage"], x["cum_obtained"]), reverse=True)
        for idx, cand in enumerate(w_cands):
            if idx > 0 and cand["cum_percentage"] == w_cands[idx - 1]["cum_percentage"]:
                cand["wing_position"] = w_cands[idx - 1]["wing_position"]
            else:
                cand["wing_position"] = idx + 1
            cand["wing_position_display"] = get_position_suffix(cand["wing_position"])
        wing_top_positions[w_lvl] = [c for c in w_cands if c.get("wing_position", 999) <= 3]

    overall_school_pass_pct = round((total_passed / total_appeared * 100), 2) if total_appeared > 0 else 0.0

    analytics = {
        "total_enrolled": total_enrolled,
        "total_appeared": total_appeared,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "overall_pass_percentage": overall_school_pass_pct,
        "grades_count": school_grades_count,
        "grades_list": [{"grade": k, "count": v} for k, v in school_grades_count.items()],
    }

    return {
        "session": session,
        "exams": exams,
        "selected_wing_key": selected_wing_key,
        "wing_label": wing_info["label"],
        "class_cumulative_rows": class_cumulative_rows,
        "school_top_position_holders": school_top_position_holders,
        "school_top_10": school_top_10,
        "wing_top_positions": wing_top_positions,
        "analytics": analytics,
        "school_setting": school_setting,
    }


@login_required
def consolidated_annual_result(request):
    """
    Cumulative Annual Result Hub across all terms (1st Term, Mid Term, Final Term).
    Displays School-Level, Wing-Level, and Class-Level Top Position Holders and School-Wide Pass Analytics.
    """
    sessions = AcademicSession.objects.all().order_by("-start_date")
    session_id = request.GET.get("session_id")
    selected_session = AcademicSession.objects.filter(id=session_id).first() if session_id else sessions.filter(is_active=True).first() or sessions.first()

    selected_wing = request.GET.get("wing", "all")
    if selected_wing not in WING_MAP:
        selected_wing = "all"

    selected_class_id = request.GET.get("class_id") or ""

    classes = ClassLevel.objects.all().order_by("id")
    if WING_MAP.get(selected_wing, {}).get("levels"):
        classes = classes.filter(level__in=WING_MAP[selected_wing]["levels"])

    data = _get_consolidated_annual_data(selected_session, selected_wing, selected_class_id if selected_class_id else None) if selected_session else None

    context = {
        "sessions": sessions,
        "selected_session": selected_session,
        "selected_wing": selected_wing,
        "selected_class_id": selected_class_id,
        "classes": classes,
        "wing_options": [{"key": k, "label": v["label"]} for k, v in WING_MAP.items()],
        "data": data,
    }
    return render(request, "exams/consolidated_annual_result.html", context)


@login_required
def print_consolidated_annual_result(request):
    """
    Official Printable / PDF Master Sheet for Consolidated Annual Results.
    """
    session_id = request.GET.get("session_id")
    selected_session = get_object_or_404(AcademicSession, pk=session_id) if session_id else AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    selected_wing = request.GET.get("wing", "all")
    selected_class_id = request.GET.get("class_id") or ""

    data = _get_consolidated_annual_data(selected_session, selected_wing, selected_class_id if selected_class_id else None)

    context = {
        "selected_session": selected_session,
        "data": data,
        "print_date": timezone.now().date(),
    }
    return render(request, "exams/print_consolidated_annual_result.html", context)


@login_required
def export_consolidated_annual_excel(request):
    """
    Exports Consolidated All-Terms Annual Master Result to Excel.
    """
    session_id = request.GET.get("session_id")
    selected_session = get_object_or_404(AcademicSession, pk=session_id) if session_id else AcademicSession.objects.filter(is_active=True).first()
    selected_wing = request.GET.get("wing", "all")
    selected_class_id = request.GET.get("class_id") or ""

    data = _get_consolidated_annual_data(selected_session, selected_wing, selected_class_id if selected_class_id else None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Annual Cumulative Result"

    title_banner = f"{data['school_setting'].name if data['school_setting'] else 'KMS'} — Annual Cumulative Master Sheet ({selected_session.name})"
    total_cols = 5 + (len(data["exams"]) * 2) + 4
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    banner = ws.cell(row=1, column=1, value=title_banner)
    banner.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    banner.fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    banner.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    headers = ["S#", "Adm #", "Student Name", "Father's Name", "Class"]
    for ex in data["exams"]:
        headers.extend([f"{ex.name} (Obt)", f"{ex.name} (%)"])
    headers.extend(["Cum. Obtained", "Cum. Max", "Overall %", "Grade", "Class Pos", "Status"])

    for col_i, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col_i, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = get_thin_border()
    ws.row_dimensions[2].height = 28

    curr_row = 3
    sr_counter = 1
    for cl_data in data["class_cumulative_rows"]:
        cl = cl_data["class_level"]
        for rec in cl_data["student_records"]:
            s = rec["student"]
            row_data = [sr_counter, s.admission_no, s.full_name, s.father_name, cl.name]
            for td in rec["term_details"]:
                row_data.append(td["obtained"] if td["appeared"] else "-")
                row_data.append(f"{td['percentage']}%" if td["appeared"] else "-")
            row_data.extend([
                rec["cum_obtained"],
                rec["cum_max"],
                f"{rec['cum_percentage']}%",
                rec["cum_grade"],
                rec["class_position_display"],
                rec["final_status"],
            ])
            for col_i, val in enumerate(row_data, 1):
                cell = ws.cell(row=curr_row, column=col_i, value=val)
                cell.border = get_thin_border()
                cell.alignment = Alignment(horizontal="center" if col_i not in (3, 4) else "left", vertical="center")
            curr_row += 1
            sr_counter += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"Annual_Cumulative_Result_{selected_session.name}.xlsx".replace(" ", "_")
    return excel_download_response(output, filename)


# ==============================================================================
# 3. STUDENT MULTI-TERM ACADEMIC EXAM HISTORY / TRANSCRIPT
# ==============================================================================

@login_required
def student_exam_history(request, student_id=None):
    """
    Complete Multi-Term Examination History and Academic Progress Report for a student.
    Shows term-by-term breakdown (1st Term, Mid Term, Final Term), subject marks, %ages,
    grades, position history, and overall pass/fail trajectory.
    """
    students_list = Student.objects.filter(status="Active").select_related("current_class", "current_section").order_by("admission_no")

    selected_student = None
    if student_id:
        selected_student = get_object_or_404(Student, pk=student_id)
    else:
        q_adm = request.GET.get("admission_no", "").strip()
        q_std = request.GET.get("student_id", "").strip()
        if q_std:
            selected_student = Student.objects.filter(id=q_std).first()
        elif q_adm:
            selected_student = Student.objects.filter(admission_no=q_adm).first()
        if not selected_student:
            selected_student = students_list.first()

    exam_records = []
    trajectory = []
    school_setting = SchoolSetting.objects.first()
    pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0

    total_exams_appeared = 0
    total_exams_passed = 0
    cum_all_obtained = 0.0
    cum_all_max = 0.0

    if selected_student:
        # Get all distinct exams where this student has marks recorded
        distinct_exams = Exam.objects.filter(
            marks__student=selected_student
        ).distinct().order_by("session__start_date", "created_at", "id")

        for ex in distinct_exams:
            total_exams_appeared += 1
            marks = ExamMark.objects.filter(
                exam=ex, student=selected_student
            ).select_related("subject", "class_level").order_by("subject__order", "subject__name")

            cl = marks.first().class_level if marks.exists() else selected_student.current_class

            # Compute student's position in that class for that exam
            class_subjects, g_max, st_records, stats = compute_class_result_matrix(ex, cl)
            st_in_matrix = next((r for r in st_records if r["student"].id == selected_student.id), None)

            obtained_sum = sum(float(m.obtained_marks) for m in marks if not m.is_absent)
            max_sum = sum(float(m.total_marks) for m in marks)
            if max_sum <= 0:
                max_sum = float(g_max)

            term_pct = st_in_matrix["percentage"] if (st_in_matrix and st_in_matrix["percentage"] is not None) else (round((obtained_sum / max_sum * 100), 2) if max_sum > 0 else 0.0)
            term_grade = st_in_matrix["grade"] if st_in_matrix else calculate_grade(term_pct, passing_pct=pass_pct)
            term_pos = st_in_matrix["position_display"] if st_in_matrix else "-"
            term_status = st_in_matrix["status"] if st_in_matrix else ("Pass" if term_pct >= pass_pct else "Fail")

            if term_status == "Pass":
                total_exams_passed += 1

            cum_all_obtained += obtained_sum
            cum_all_max += max_sum

            # Subject breakdown list
            subj_list = []
            for m in marks:
                s_pct = m.percentage
                s_status = "Pass" if not m.is_absent and m.obtained_marks >= (m.total_marks * Decimal(str(pass_pct / 100.0))) else "Fail"
                subj_list.append({
                    "subject": m.subject,
                    "obtained": "A" if m.is_absent else (int(m.obtained_marks) if m.obtained_marks % 1 == 0 else m.obtained_marks),
                    "total": int(m.total_marks) if m.total_marks % 1 == 0 else m.total_marks,
                    "percentage": s_pct,
                    "is_absent": m.is_absent,
                    "status": s_status,
                })

            exam_records.append({
                "exam": ex,
                "class_level": cl,
                "subjects": subj_list,
                "obtained_sum": obtained_sum,
                "max_sum": max_sum,
                "percentage": term_pct,
                "grade": term_grade,
                "position": term_pos,
                "status": term_status,
            })

            trajectory.append({
                "exam_name": ex.name,
                "percentage": term_pct,
                "grade": term_grade,
                "status": term_status,
                "position": term_pos,
            })

    career_pct = round((cum_all_obtained / cum_all_max * 100), 2) if cum_all_max > 0 else 0.0
    career_grade = calculate_grade(career_pct, passing_pct=pass_pct) if cum_all_max > 0 else "-"
    success_rate = round((total_exams_passed / total_exams_appeared * 100), 1) if total_exams_appeared > 0 else 0.0

    context = {
        "students_list": students_list,
        "selected_student": selected_student,
        "exam_records": exam_records,
        "trajectory": trajectory,
        "total_exams_appeared": total_exams_appeared,
        "total_exams_passed": total_exams_passed,
        "cum_all_obtained": cum_all_obtained,
        "cum_all_max": cum_all_max,
        "career_pct": career_pct,
        "career_grade": career_grade,
        "success_rate": success_rate,
        "school_setting": school_setting,
    }
    return render(request, "exams/student_exam_history.html", context)


@login_required
def print_student_exam_history(request, student_id):
    """
    Printable Official Academic Transcript / Student DMC History Card.
    """
    student = get_object_or_404(Student, pk=student_id)
    school_setting = SchoolSetting.objects.first()
    pass_pct = float(school_setting.passing_percentage) if (school_setting and school_setting.passing_percentage) else 30.0

    distinct_exams = Exam.objects.filter(
        marks__student=student
    ).distinct().order_by("session__start_date", "created_at", "id")

    exam_records = []
    cum_all_obtained = 0.0
    cum_all_max = 0.0

    for ex in distinct_exams:
        marks = ExamMark.objects.filter(
            exam=ex, student=student
        ).select_related("subject", "class_level").order_by("subject__order", "subject__name")

        cl = marks.first().class_level if marks.exists() else student.current_class
        class_subjects, g_max, st_records, stats = compute_class_result_matrix(ex, cl)
        st_in_matrix = next((r for r in st_records if r["student"].id == student.id), None)

        obtained_sum = sum(float(m.obtained_marks) for m in marks if not m.is_absent)
        max_sum = sum(float(m.total_marks) for m in marks)
        if max_sum <= 0:
            max_sum = float(g_max)

        term_pct = st_in_matrix["percentage"] if (st_in_matrix and st_in_matrix["percentage"] is not None) else (round((obtained_sum / max_sum * 100), 2) if max_sum > 0 else 0.0)
        term_grade = st_in_matrix["grade"] if st_in_matrix else calculate_grade(term_pct, passing_pct=pass_pct)
        term_pos = st_in_matrix["position_display"] if st_in_matrix else "-"
        term_status = st_in_matrix["status"] if st_in_matrix else ("Pass" if term_pct >= pass_pct else "Fail")

        cum_all_obtained += obtained_sum
        cum_all_max += max_sum

        subj_list = []
        for m in marks:
            subj_list.append({
                "subject": m.subject,
                "obtained": "A" if m.is_absent else (int(m.obtained_marks) if m.obtained_marks % 1 == 0 else m.obtained_marks),
                "total": int(m.total_marks) if m.total_marks % 1 == 0 else m.total_marks,
                "percentage": m.percentage,
                "is_absent": m.is_absent,
            })

        exam_records.append({
            "exam": ex,
            "class_level": cl,
            "subjects": subj_list,
            "obtained_sum": obtained_sum,
            "max_sum": max_sum,
            "percentage": term_pct,
            "grade": term_grade,
            "position": term_pos,
            "status": term_status,
        })

    career_pct = round((cum_all_obtained / cum_all_max * 100), 2) if cum_all_max > 0 else 0.0
    career_grade = calculate_grade(career_pct, passing_pct=pass_pct) if cum_all_max > 0 else "-"

    context = {
        "student": student,
        "exam_records": exam_records,
        "cum_all_obtained": cum_all_obtained,
        "cum_all_max": cum_all_max,
        "career_pct": career_pct,
        "career_grade": career_grade,
        "school_setting": school_setting,
        "print_date": timezone.now().date(),
    }
    return render(request, "exams/print_student_exam_history.html", context)


@login_required
def export_all_exams_backup_excel(request):
    """
    Exports a real, complete multi-sheet Excel backup of ALL Examinations,
    Subjects, Class Curriculum Mappings, Students, and ALL Student Exam Marks.
    Can be restored directly via import_all_exams_backup_excel or Master Restore.
    """
    from school.backup_utils import _style_worksheet

    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College"
    wb = Workbook()

    # Sheet 1: Exam_Marks (All marks across all exams, classes, and subjects)
    ws_mk = wb.active
    ws_mk.title = "Exam_Marks"
    mk_headers = [
        "Exam Name",
        "Session Name",
        "Admission No",
        "Student Full Name",
        "Father Name",
        "Class Name",
        "Section Name",
        "Subject Name",
        "Subject Code",
        "Total Marks",
        "Obtained Marks",
        "Is Absent",
        "Remarks",
    ]
    mk_rows = []
    for m in ExamMark.objects.select_related(
        "exam", "exam__session", "student", "student__current_section", "class_level", "subject"
    ).all():
        mk_rows.append([
            m.exam.name,
            m.exam.session.name if (m.exam and m.exam.session) else "",
            m.student.admission_no,
            m.student.full_name,
            m.student.father_name,
            m.class_level.name if m.class_level else "",
            m.student.current_section.name if (m.student and m.student.current_section) else "A",
            m.subject.name,
            m.subject.code,
            float(m.total_marks),
            float(m.obtained_marks),
            "Yes" if m.is_absent else "No",
            m.remarks,
        ])
    _style_worksheet(ws_mk, "Full Examination Marks Backup (All Terms & Classes)", mk_headers, mk_rows, school_name)

    # Sheet 2: Exams_Curriculum
    ws_ex = wb.create_sheet("Exams_Curriculum")
    ex_headers = [
        "Record Type",
        "Name / Exam / Subject",
        "Session / Class Name",
        "Subject Code / Start Date",
        "Total Marks / End Date",
        "Passing Marks / Is Active",
        "Order",
    ]
    ex_rows = []
    for e in Exam.objects.select_related("session").all():
        ex_rows.append([
            "EXAM",
            e.name,
            e.session.name if e.session else "",
            str(e.start_date) if e.start_date else "",
            str(e.end_date) if e.end_date else "",
            "Yes" if e.is_active else "No",
            0,
        ])
    for sub in Subject.objects.all():
        ex_rows.append([
            "SUBJECT",
            sub.name,
            "",
            sub.code,
            "",
            "Yes" if sub.is_active else "No",
            sub.order,
        ])
    for cs in ClassSubject.objects.select_related("class_level", "subject").all():
        ex_rows.append([
            "CLASS_SUBJECT",
            cs.subject.name,
            cs.class_level.name,
            cs.subject.code,
            float(cs.total_marks),
            float(cs.passing_marks),
            cs.order,
        ])
    _style_worksheet(ws_ex, "Examinations & Curriculum Setup Backup", ex_headers, ex_rows, school_name)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    ts = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M")
    return excel_download_response(buf, f"KMS_Full_Exams_And_Marks_Backup_{ts}.xlsx")


@login_required
def import_all_exams_backup_excel(request):
    """
    Restores all Examinations, Subjects, Class Curriculum, and Student Exam Marks
    from an uploaded Full Exams Backup (.xlsx) or Master Backup (.xlsx).
    """
    from school.backup_utils import restore_from_master_excel

    if request.method != "POST" or "excel_file" not in request.FILES:
        messages.error(request, "Please select a valid Exam Backup (.xlsx) file to restore.")
        return redirect("exam_dashboard")

    excel_file = request.FILES["excel_file"]
    try:
        ok, msg = restore_from_master_excel(excel_file)
        if ok:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
    except Exception as e:
        messages.error(request, f"Exam Marks Backup Restore failed: {str(e)}")

    return redirect("exam_dashboard")






