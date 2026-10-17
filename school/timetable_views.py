import json
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from exams.models import Subject
from school.models import AcademicSession, ClassLevel, TimetableEntry, TimetablePeriod, SchoolSetting
from teachers.models import Teacher
from .timetable_utils import (
    detect_timetable_clashes,
    ensure_timetable_periods,
    seed_real_school_timetable,
)


@login_required
def timetable_dashboard(request):
    """
    Main School Master Timetable Dashboard:
    - Primary Wing (Nursery, Prep, Class 1-5) matching the Pink Board
    - Middle, High & Higher Secondary Wing (6th, 7th, 8th, 9th, 10th, 1st & 2nd Year) matching the Green Board
    - Master All-Class Grid
    - Interactive Clash / Double-Booking Detection & Real-time Warning
    - Teacher-wise filter
    """
    ensure_timetable_periods()
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    # Pre-seed if empty
    if not TimetableEntry.objects.exists():
        seed_real_school_timetable(force=True)

    wing = request.GET.get("wing", "primary").strip().lower()
    selected_teacher_id = request.GET.get("teacher_id", "").strip()

    periods = list(TimetablePeriod.objects.all().order_by("order", "period_number"))

    # Order and filter classes
    all_classes = list(ClassLevel.objects.all())
    # Sort classes logically from Nursery up to 2nd Year
    order_weights = {
        "Nursery": 1, "Nur": 1, "Prep": 2, "K.G": 2, "KG": 2,
        "Class 1": 3, "1st": 3, "Class 2": 4, "2nd": 4,
        "Class 3": 5, "3rd": 5, "Class 4": 6, "4th": 6,
        "Class 5": 7, "5th": 7, "Class 6": 8, "6th": 8,
        "Class 7": 9, "7th": 9, "Class 8": 10, "8th": 10,
        "Class 9": 11, "9th": 11, "Class 10": 12, "10th": 12,
        "1st Year Pre-Medical": 13, "1st Year Pre-Engineering": 14, "ICS 1st Year": 15, "1st Year": 16,
        "2nd Year Pre-Medical": 17, "2nd Year Pre-Engineering": 18, "ICS 2nd Year": 19, "2nd Year": 20,
    }
    all_classes.sort(key=lambda c: order_weights.get(c.name, 99))

    primary_levels = ["Prep", "Primary"]
    middle_high_levels = ["Middle", "High", "Higher Secondary"]

    if wing == "primary":
        classes = [c for c in all_classes if c.level in primary_levels or any(x in c.name for x in ["Nur", "Prep", "1", "2", "3", "4", "5"]) and not any(x in c.name for x in ["10", "1st", "15"])]
        wing_title = "Primary Section Timetable (Nursery – 5th)"
        board_theme = "pink"
    elif wing == "middle_high":
        classes = [c for c in all_classes if c.level in middle_high_levels and not any(x in c.name for x in ["Nursery", "Prep", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])]
        # Filter down duplicates of 1st year / 2nd year if multiple exist
        seen_names = set()
        filtered_mh = []
        for c in classes:
            base_name = "1st Year" if "1st Year" in c.name else ("2nd Year" if "2nd Year" in c.name else c.name)
            if base_name in ["1st Year", "2nd Year"]:
                if base_name not in seen_names:
                    seen_names.add(base_name)
                    filtered_mh.append(c)
            else:
                filtered_mh.append(c)
        classes = filtered_mh
        wing_title = "Middle, High & College Timetable (6th – 2nd Year)"
        board_theme = "green"
    else:
        # All classes
        classes = all_classes
        wing_title = "School Master Timetable (All Classes)"
        board_theme = "default"

    # Fetch all entries
    entries_qs = TimetableEntry.objects.select_related("period", "class_level", "teacher", "subject")
    if active_session:
        entries_qs = entries_qs.filter(academic_session=active_session)

    # Detect clashes
    clashes_by_period, clashes_list, clash_entry_ids = detect_timetable_clashes(active_session)

    # Build matrix: grid[period_id][class_id] = entry
    grid = defaultdict(dict)
    for entry in entries_qs:
        grid[entry.period_id][entry.class_level_id] = entry

    all_teachers = Teacher.objects.filter(status="Active").order_by("full_name")
    if not all_teachers.exists():
        all_teachers = Teacher.objects.all().order_by("full_name")

    all_subjects = Subject.objects.all().order_by("name")

    # If teacher view requested
    selected_teacher = None
    teacher_schedule = []
    if selected_teacher_id:
        try:
            selected_teacher = Teacher.objects.get(id=int(selected_teacher_id))
            for p in periods:
                t_entries = list(entries_qs.filter(period=p, teacher=selected_teacher))
                teacher_schedule.append({
                    "period": p,
                    "entries": t_entries,
                    "is_free": len(t_entries) == 0 and not p.is_break,
                    "has_clash": len(t_entries) > 1,
                })
        except Exception:
            selected_teacher = None

    context = {
        "periods": periods,
        "classes": classes,
        "grid": grid,
        "wing": wing,
        "wing_title": wing_title,
        "board_theme": board_theme,
        "clashes_list": clashes_list,
        "clash_entry_ids": clash_entry_ids,
        "all_teachers": all_teachers,
        "all_subjects": all_subjects,
        "active_session": active_session,
        "selected_teacher": selected_teacher,
        "selected_teacher_id": selected_teacher_id,
        "teacher_schedule": teacher_schedule,
    }
    return render(request, "school/timetable/dashboard.html", context)


@login_required
@require_POST
def api_update_timetable_cell(request):
    """
    AJAX endpoint to assign or update a single timetable slot.
    Allows changing Teacher or Subject with real-time clash warning.
    """
    try:
        data = json.loads(request.body)
        class_id = int(data.get("class_id"))
        period_id = int(data.get("period_id"))
        teacher_id = data.get("teacher_id")
        subject_id = data.get("subject_id")
        custom_subject = data.get("custom_subject", "").strip()
        custom_teacher = data.get("custom_teacher", "").strip()
        day_of_week = data.get("day_of_week", "Daily")

        active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
        cl = get_object_or_404(ClassLevel, id=class_id)
        p = get_object_or_404(TimetablePeriod, id=period_id)

        teacher_obj = Teacher.objects.filter(id=int(teacher_id)).first() if teacher_id else None
        subject_obj = Subject.objects.filter(id=int(subject_id)).first() if subject_id else None

        entry, created = TimetableEntry.objects.update_or_create(
            academic_session=active_session,
            class_level=cl,
            period=p,
            day_of_week=day_of_week,
            defaults={
                "teacher": teacher_obj,
                "custom_teacher": custom_teacher if not teacher_obj else "",
                "subject": subject_obj,
                "custom_subject": custom_subject if not subject_obj else "",
            }
        )

        # Check for clashes in this period
        clash_warning = ""
        has_clash = False
        t_key = teacher_obj.id if teacher_obj else (custom_teacher.upper() if custom_teacher else None)
        if t_key and not p.is_break:
            other_entries = TimetableEntry.objects.filter(
                academic_session=active_session,
                period=p,
                day_of_week=day_of_week,
            ).exclude(class_level=cl)

            if teacher_obj:
                other_entries = other_entries.filter(teacher=teacher_obj)
            else:
                other_entries = other_entries.filter(custom_teacher__iexact=custom_teacher)

            if other_entries.exists():
                has_clash = True
                other_classes = ", ".join([e.class_level.name for e in other_entries])
                t_name = entry.get_teacher_name()
                clash_warning = f"Warning: {t_name} is already assigned to {other_classes} in Period {p.name}!"

        return JsonResponse({
            "success": True,
            "entry_id": entry.id,
            "subject_name": entry.get_subject_name(),
            "teacher_name": entry.get_teacher_name(),
            "has_clash": has_clash,
            "clash_warning": clash_warning,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@login_required
def timetable_print_view(request):
    """
    High-resolution 1-Page Landscape Printable View:
    Matches school paper/board charts (Pink for Primary, Green for Middle/High/College, or All).
    Specifically styled for office printers (A4 / Legal Landscape) with signatures.
    """
    ensure_timetable_periods()
    active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
    school_setting = SchoolSetting.objects.first()

    wing = request.GET.get("wing", "primary").strip().lower()
    selected_teacher_id = request.GET.get("teacher_id", "").strip()

    periods = list(TimetablePeriod.objects.all().order_by("order", "period_number"))
    all_classes = list(ClassLevel.objects.all())

    order_weights = {
        "Nursery": 1, "Nur": 1, "Prep": 2, "K.G": 2, "KG": 2,
        "Class 1": 3, "1st": 3, "Class 2": 4, "2nd": 4,
        "Class 3": 5, "3rd": 5, "Class 4": 6, "4th": 6,
        "Class 5": 7, "5th": 7, "Class 6": 8, "6th": 8,
        "Class 7": 9, "7th": 9, "Class 8": 10, "8th": 10,
        "Class 9": 11, "9th": 11, "Class 10": 12, "10th": 12,
        "1st Year Pre-Medical": 13, "1st Year Pre-Engineering": 14, "ICS 1st Year": 15, "1st Year": 16,
        "2nd Year Pre-Medical": 17, "2nd Year Pre-Engineering": 18, "ICS 2nd Year": 19, "2nd Year": 20,
    }
    all_classes.sort(key=lambda c: order_weights.get(c.name, 99))

    primary_levels = ["Prep", "Primary"]
    middle_high_levels = ["Middle", "High", "Higher Secondary"]

    if wing == "primary":
        classes = [c for c in all_classes if c.level in primary_levels or any(x in c.name for x in ["Nur", "Prep", "1", "2", "3", "4", "5"]) and not any(x in c.name for x in ["10", "1st", "15"])]
        wing_title = "PRIMARY SECTION MASTER TIMETABLE"
        theme_class = "theme-pink"
    elif wing == "middle_high":
        classes = [c for c in all_classes if c.level in middle_high_levels and not any(x in c.name for x in ["Nursery", "Prep", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])]
        seen_names = set()
        filtered_mh = []
        for c in classes:
            base_name = "1st Year" if "1st Year" in c.name else ("2nd Year" if "2nd Year" in c.name else c.name)
            if base_name in ["1st Year", "2nd Year"]:
                if base_name not in seen_names:
                    seen_names.add(base_name)
                    filtered_mh.append(c)
            else:
                filtered_mh.append(c)
        classes = filtered_mh
        wing_title = "MIDDLE, HIGH & HIGHER SECONDARY SECTION TIMETABLE"
        theme_class = "theme-green"
    else:
        classes = all_classes
        wing_title = "SCHOOL MASTER TIMETABLE"
        theme_class = "theme-default"

    entries_qs = TimetableEntry.objects.select_related("period", "class_level", "teacher", "subject")
    if active_session:
        entries_qs = entries_qs.filter(academic_session=active_session)

    grid = defaultdict(dict)
    for entry in entries_qs:
        grid[entry.period_id][entry.class_level_id] = entry

    # Teacher specific print if requested
    selected_teacher = None
    teacher_schedule = []
    if selected_teacher_id:
        try:
            selected_teacher = Teacher.objects.get(id=int(selected_teacher_id))
            wing_title = f"INDIVIDUAL TEACHER TIMETABLE — {selected_teacher.full_name}"
            for p in periods:
                t_entries = list(entries_qs.filter(period=p, teacher=selected_teacher))
                teacher_schedule.append({
                    "period": p,
                    "entries": t_entries,
                    "is_free": len(t_entries) == 0 and not p.is_break,
                })
        except Exception:
            selected_teacher = None

    context = {
        "periods": periods,
        "classes": classes,
        "grid": grid,
        "wing": wing,
        "wing_title": wing_title,
        "theme_class": theme_class,
        "active_session": active_session,
        "school_setting": school_setting,
        "selected_teacher": selected_teacher,
        "teacher_schedule": teacher_schedule,
    }
    return render(request, "school/timetable/print_landscape.html", context)


@login_required
def api_reset_default_timetable(request):
    """
    1-Click reset to reload the official school timetable from the original photo charts.
    """
    if request.method == "POST":
        TimetableEntry.objects.all().delete()
        seed_real_school_timetable(force=True)
        messages.success(request, "Timetable successfully reloaded from the official school charts!")
        return redirect("timetable_dashboard")
    return redirect("timetable_dashboard")
