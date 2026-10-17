from collections import defaultdict
from school.models import AcademicSession, ClassLevel, TimetablePeriod, TimetableEntry
from teachers.models import Teacher
from exams.models import Subject


def ensure_timetable_periods():
    """
    Ensures standard periods 01 to 08 + Break are present.
    Matching the school boards:
    01 (08:00 - 08:45)
    02 (08:45 - 09:30)
    03 (09:30 - 10:15)
    04 (10:15 - 11:00)
    05 (11:00 - 11:45)
    Break (11:45 - 12:15)
    06 (12:15 - 01:00)
    07 (01:00 - 01:45)
    08 (01:45 - 02:30)
    """
    period_defs = [
        {"period_number": 1, "name": "01", "start_time": "08:00 AM", "end_time": "08:45 AM", "is_break": False, "order": 1},
        {"period_number": 2, "name": "02", "start_time": "08:45 AM", "end_time": "09:30 AM", "is_break": False, "order": 2},
        {"period_number": 3, "name": "03", "start_time": "09:30 AM", "end_time": "10:15 AM", "is_break": False, "order": 3},
        {"period_number": 4, "name": "04", "start_time": "10:15 AM", "end_time": "11:00 AM", "is_break": False, "order": 4},
        {"period_number": 5, "name": "05", "start_time": "11:00 AM", "end_time": "11:45 AM", "is_break": False, "order": 5},
        {"period_number": 0, "name": "Break", "start_time": "11:45 AM", "end_time": "12:15 PM", "is_break": True, "order": 6},
        {"period_number": 6, "name": "06", "start_time": "12:15 PM", "end_time": "01:00 PM", "is_break": False, "order": 7},
        {"period_number": 7, "name": "07", "start_time": "01:00 PM", "end_time": "01:45 PM", "is_break": False, "order": 8},
        {"period_number": 8, "name": "08", "start_time": "01:45 PM", "end_time": "02:30 PM", "is_break": False, "order": 9},
    ]
    periods = []
    for d in period_defs:
        p, _ = TimetablePeriod.objects.get_or_create(
            name=d["name"],
            defaults=d
        )
        periods.append(p)
    return periods


def get_teacher_by_keyword(kw):
    if not kw:
        return None
    kw_clean = kw.strip().upper()
    return (
        Teacher.objects.filter(full_name__icontains=kw_clean).first()
        or Teacher.objects.filter(full_name__icontains=kw_clean.split()[-1]).first()
    )


def get_subject_by_keyword(kw):
    if not kw:
        return None
    kw_clean = kw.strip()
    return (
        Subject.objects.filter(name__iexact=kw_clean).first()
        or Subject.objects.filter(name__icontains=kw_clean).first()
    )


def detect_timetable_clashes(session=None):
    """
    Scans all timetable entries to find any teacher assigned to more than 1 class
    in the SAME period (Duplicate period warning).
    Returns:
      clashes_by_period: { period_id: { teacher_id_or_name: [entry1, entry2, ...] } }
      clashes_list: [ {'period': p, 'teacher': t_name, 'classes': [c1, c2, ...]}, ... ]
      clash_entry_ids: set of entry.id that have conflicts
    """
    entries = TimetableEntry.objects.select_related("period", "class_level", "teacher", "subject")
    if session:
        entries = entries.filter(academic_session=session)

    # Exclude break periods
    entries = entries.filter(period__is_break=False)

    teacher_period_map = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        t_key = entry.teacher_id if entry.teacher_id else (entry.custom_teacher.strip().upper() if entry.custom_teacher else None)
        if t_key:
            teacher_period_map[entry.period_id][t_key].append(entry)

    clashes_by_period = defaultdict(dict)
    clashes_list = []
    clash_entry_ids = set()

    for pid, teachers in teacher_period_map.items():
        for t_key, entry_list in teachers.items():
            if len(entry_list) > 1:
                clashes_by_period[pid][t_key] = entry_list
                for e in entry_list:
                    clash_entry_ids.add(e.id)
                first_e = entry_list[0]
                clashes_list.append({
                    "period": first_e.period,
                    "teacher_name": first_e.get_teacher_name(),
                    "classes": [e.class_level.name for e in entry_list],
                    "entries": entry_list,
                })

    return clashes_by_period, clashes_list, clash_entry_ids


def seed_real_school_timetable(force=False):
    """
    Populates the exact timetable from the provided school photo charts:
    - Pink Chart (Primary: Nursery, Prep/KG, 1st, 2nd, 3rd, 4th, 5th)
    - Green Chart (Middle, High, Higher: 6th, 7th, 8th, 9th, 10th, 1st Year, 2nd Year)
    """
    if TimetableEntry.objects.exists() and not force:
        return

    periods_map = {p.period_number: p for p in ensure_timetable_periods()}
    session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()

    # Teachers map
    teachers = {t.full_name: t for t in Teacher.objects.all()}

    def find_t(name_sub):
        for full, obj in teachers.items():
            if name_sub.upper() in full:
                return obj
        return None

    # Classes
    c_nur = ClassLevel.objects.filter(name__icontains="Nursery").first()
    c_prep = ClassLevel.objects.filter(name__icontains="Prep").first()
    c_1st = ClassLevel.objects.filter(name__icontains="Class 1").first()
    c_2nd = ClassLevel.objects.filter(name__icontains="Class 2").first()
    c_3rd = ClassLevel.objects.filter(name__icontains="Class 3").first()
    c_4th = ClassLevel.objects.filter(name__icontains="Class 4").first()
    c_5th = ClassLevel.objects.filter(name__icontains="Class 5").first()
    c_6th = ClassLevel.objects.filter(name__icontains="Class 6").first()
    c_7th = ClassLevel.objects.filter(name__icontains="Class 7").first()
    c_8th = ClassLevel.objects.filter(name__icontains="Class 8").first()
    c_9th = ClassLevel.objects.filter(name__icontains="Class 9").first()
    c_10th = ClassLevel.objects.filter(name__icontains="Class 10").first()
    c_1st_yr = ClassLevel.objects.filter(name__icontains="1st Year").first()
    c_2nd_yr = ClassLevel.objects.filter(name__icontains="2nd Year").first()

    # Pink Board Data (Primary)
    pink_board = {
        c_nur: {
            1: ("Nazera", "ATTA UR RAHMAN"),
            2: ("Maths Writing", "SHER WALI"),
            3: ("English Writing", "NADIM KHAN"),
            4: ("Urdu Writing", "NISAR AHMAD"),
            5: ("English Reading", "SAJID ULLAH"),
            6: ("Urdu Writing", "SHER WALI"),
            7: ("Urdu Reading", "UMAR SYED KHAN"),
            8: ("Hand Writing", "UMAR SYED KHAN"),
        },
        c_prep: {
            1: ("Maths (Oral)", "SHER WALI"),
            2: ("Nazira", "NAIK ZADA"),
            3: ("Urdu Writing", "IKRAM ULLAH"),
            4: ("English Writing", "SALMAN KHAN"),
            5: ("English Reading", "NADIM KHAN"),
            6: ("Urdu Reading", "NADIM KHAN"),
            7: ("General Knowledge", "UMAR SYED KHAN"),
            8: ("Hand Writing", "IKRAM ULLAH"),
        },
        c_1st: {
            1: ("General Knowledge", "SAJID ULLAH"),
            2: ("Mathematics", "NADIM KHAN"),
            3: ("Nazira", "ATTA UR RAHMAN"),
            4: ("English + Hand Writing", "SHER WALI"),
            5: ("Urdu + Hand Writing", "SHER WALI"),
            6: ("English Grammar", "SALMAN KHAN"),
            7: ("Islamyat", "SHER WALI"),
            8: ("Hand Writing", "UMAR SYED KHAN"),
        },
        c_2nd: {
            1: ("English", "IKRAM ULLAH"),
            2: ("Nazira", "ATTA UR RAHMAN"),
            3: ("Urdu + Hand Writing", "NISAR AHMAD"),
            4: ("General Knowledge", "NADIM KHAN"),
            5: ("Mathematics", "NISAR AHMAD"),
            6: ("Islamyat", "KHAIR UR RAHMAN"),
            7: ("English Grammar", "IKRAM ULLAH"),
            8: ("Hand Writing", "NADIM KHAN"),
        },
        c_3rd: {
            1: ("General Knowledge", "SALMAN KHAN"),
            2: ("Mathematics", "NISAR AHMAD"),
            3: ("Nazira", "RAHMAN ALI"),
            4: ("English + Hand Writing", "IKRAM ULLAH"),
            5: ("Islamyat", "KHAIR UR RAHMAN"),
            6: ("Urdu + Hand Writing", "SAJID ULLAH"),
            7: ("English Grammar", "SALMAN KHAN"),
            8: ("Hand Writing", "IKRAM ULLAH"),
        },
        c_4th: {
            1: ("Mathematics", "NISAR AHMAD"),
            2: ("English + Hand Writing", "IKRAM ULLAH"),
            3: ("General Science", "SALMAN KHAN"),
            4: ("Nazira", "RAHMAN ALI"),
            5: ("Urdu + Hand Writing", "SHER WALI"),
            6: ("Islamyat", "UMAR SYED KHAN"),
            7: ("Pakistan Studies", "NADIM KHAN"),
            8: ("English Grammar", "SHER WALI"),
        },
        c_5th: {
            1: ("Pakistan Studies", "RAHMAN ALI"),
            2: ("Urdu + Grammar", "KHAIR UR RAHMAN"),
            3: ("English + Hand Writing", "SAJID ULLAH"),
            4: ("Islamyat", "ATTA UR RAHMAN"),
            5: ("Nazira", "RAHMAN ALI"),
            6: ("General Science", "ISRAR AHMAD"),
            7: ("Mathematics", "NISAR AHMAD"),
            8: ("English Grammar", "SALMAN KHAN"),
        },
    }

    # Green Board Data (Middle, High, Higher Secondary)
    green_board = {
        c_6th: {
            1: ("Islamyat", "KHAIR UR RAHMAN"),
            2: ("General Science", "SALMAN KHAN"),
            3: ("Nazira", "NAIK ZADA"),
            4: ("English", "SAJID ULLAH"),
            5: ("Pakistan Studies", "IKRAM ULLAH"),
            6: ("Mathematics", "NISAR AHMAD"),
            7: ("Urdu", "ATTA UR RAHMAN"),
            8: ("English Grammar", "SALMAN KHAN"),
        },
        c_7th: {
            1: ("Nazira", "NAIK ZADA"),
            2: ("English", "SAJID ULLAH"),
            3: ("General Science", "USMAN GHANI"),
            4: ("Islamyat", "KHAIR UR RAHMAN"),
            5: ("English Grammar", "SHAFI UR RAHMAN"),
            6: ("Pakistan Studies", "ATTA UR RAHMAN"),
            7: ("Urdu", "RAHMAN ALI"),
            8: ("Mathematics", "NISAR AHMAD"),
        },
        c_8th: {
            1: ("Urdu", "RAHMAN ALI"),
            2: ("Mathematics", "MUHAMMAD ISLAM"),
            3: ("Mutalae Quran", "KHAIR UR RAHMAN"),
            4: ("Chemistry", "MUHAMMAD ISLAM"),
            5: ("Biology", "ISRAR AHMAD"),
            6: ("English", "SHAFI UR RAHMAN"),
            7: ("Physics", "USMAN GHANI"),
            8: ("English Grammar", "SAJID ULLAH"),
        },
        c_9th: {
            1: ("Physics", "MUHAMMAD ISLAM"),
            2: ("Urdu + Pak Studies", "RAHMAN ALI"),
            3: ("Biology", "ISRAR AHMAD"),
            4: ("English", "SHAFI UR RAHMAN"),
            5: ("Quran + Islamyat", "NAIK ZADA"),
            6: ("Mathematics", "USMAN GHANI"),
            7: ("Chemistry", "MUHAMMAD ISLAM"),
            8: ("English Grammar", "ISRAR AHMAD"),
        },
        c_10th: {
            1: ("Biology", "ISRAR AHMAD"),
            2: ("Chemistry", "USMAN GHANI"),
            3: ("English", "SHAFI UR RAHMAN"),
            4: ("Mathematics", "USMAN GHANI"),
            5: ("Urdu + Pak Studies", "FARMAN ALI"),
            6: ("Physics", "MUHAMMAD ISLAM"),
            7: ("Quran + Islamyat", "NAIK ZADA"),
            8: ("English Grammar", "MUHAMMAD ISLAM"),
        },
        c_1st_yr: {
            1: ("Physics", "USMAN GHANI"),
            2: ("English", "SHAFI UR RAHMAN"),
            3: ("Urdu", "FARMAN ALI"),
            4: ("Biology", "ISRAR AHMAD"),
            5: ("Chemistry", "MUHAMMAD ISLAM"),
            6: ("Quran + Islamyat", "RAHMAN ALI"),
            7: ("Islamyat", "KHAIR UR RAHMAN"),
            8: ("Library / Self Study", "FARMAN ALI"),
        },
        c_2nd_yr: {
            1: ("English", "SHAFI UR RAHMAN"),
            2: ("Biology", "ISRAR AHMAD"),
            3: ("Chemistry", "MUHAMMAD ISLAM"),
            4: ("Mutalae Quran", "NAIK ZADA"),
            5: ("Physics", "USMAN GHANI"),
            6: ("Urdu + Pak Studies", "FARMAN ALI"),
            7: ("Pakistan Studies", "FARMAN ALI"),
            8: ("Library / Self Study", "FARMAN ALI"),
        },
    }

    all_boards = {**pink_board, **green_board}

    for cl, periods_data in all_boards.items():
        if not cl:
            continue
        for p_num, (subj_text, teacher_kw) in periods_data.items():
            period_obj = periods_map.get(p_num)
            if not period_obj:
                continue

            t_obj = find_t(teacher_kw)
            s_obj = get_subject_by_keyword(subj_text)

            TimetableEntry.objects.update_or_create(
                academic_session=session,
                class_level=cl,
                period=period_obj,
                day_of_week="Daily",
                defaults={
                    "subject": s_obj,
                    "custom_subject": subj_text if not s_obj else "",
                    "teacher": t_obj,
                    "custom_teacher": teacher_kw if not t_obj else "",
                }
            )
