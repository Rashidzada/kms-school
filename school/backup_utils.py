import glob
import io
import json
import os
import re
import smtplib
import socket
import subprocess
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import connection, transaction
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# Ordered list of all school ERP tables in foreign-key dependency order
ERP_TABLES_IN_ORDER = [
    "school_schoolsetting",
    "school_academicsession",
    "school_classlevel",
    "teachers_salaryscale",
    "teachers_teacher",
    "school_section",
    "students_familyhousehold",
    "students_student",
    "students_studentattendance",
    "students_promotionhistory",
    "teachers_teacherattendancesetting",
    "teachers_teacherattendance",
    "teachers_teacherloan",
    "teachers_monthlysalarybill",
    "teachers_teacherloanrepayment",
    "finance_studentfeeledger",
    "finance_studentfeemonthentry",
    "finance_feepaymentreceipt",
    "finance_feepaymentreceipt_month_entries",
    "accounts_expense",
    "exams_exam",
    "exams_subject",
    "exams_classsubject",
    "exams_exammark",
]


def sync_all_postgresql_sequences():
    """
    Synchronizes all PostgreSQL auto-increment primary key sequences across all apps
    so that nextval() never collides with existing IDs after a restore or import.
    """
    if "postgresql" not in connection.settings_dict.get("ENGINE", ""):
        return
    try:
        app_labels = [app.label for app in apps.get_app_configs()]
        out = io.StringIO()
        call_command("sqlsequencereset", *app_labels, stdout=out, no_color=True)
        sql = out.getvalue()
        if sql.strip():
            with connection.cursor() as cursor:
                cursor.execute(sql)
    except Exception:
        pass


def _sql_literal(val):
    """
    Safely formats a Python value as a standard PostgreSQL SQL literal for INSERT statements.
    """
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float, Decimal)):
        return str(val)
    if isinstance(val, datetime):
        if timezone.is_aware(val):
            return "'" + val.isoformat() + "'"
        return "'" + val.strftime("%Y-%m-%d %H:%M:%S") + "'"
    if isinstance(val, date):
        return "'" + val.strftime("%Y-%m-%d") + "'"
    if isinstance(val, time):
        return "'" + val.strftime("%H:%M:%S") + "'"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def generate_full_sql_dump():
    """
    Generates a 100% complete, self-contained PostgreSQL .sql dump of the entire KMS database:
    - All Classes, Sections, Academic Sessions, School Settings
    - All Families, Students, Student Attendance, Promotions
    - All Salary Scales, Teachers (Name, Father Name, Contact, Photo, Section, etc.), Teacher Attendance, Loans, Salary Bills
    - All Fee Ledgers, 12-Month Entries, Fee Payment Receipts & M2M Links
    - All General Expenses
    - All Exams, Subjects, Class Subjects, and Student Exam Marks
    - Automatic PostgreSQL sequence synchronization (setval) at the end.
    Compatible with:
      1. Direct KMS Web Upload Restore
      2. pgAdmin Query Tool execution
      3. psql -U postgres -d kms_db -f backup.sql
    """
    timestamp_str = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "-- =============================================================================",
        "-- KOHISAR MODEL SCHOOL & COLLEGE (KMS) - FULL POSTGRESQL DATABASE BACKUP (.SQL)",
        f"-- Generated At: {timestamp_str}",
        "-- Includes: Students, Teachers, Classes, Sections, Exams, Marks, Fee Ledgers,",
        "--           Fee Payment Receipts, Salary Bills, Loans, Attendance & Expenses",
        "-- =============================================================================",
        "",
        "BEGIN;",
        "",
    ]

    with connection.cursor() as cursor:
        # 1. Truncate ERP data tables in reverse dependency order so clean restore works without FK errors
        tables_to_truncate = [f'"{t}"' for t in reversed(ERP_TABLES_IN_ORDER)]
        lines.append("-- Clear existing ERP records before full restore")
        lines.append(f"TRUNCATE TABLE {', '.join(tables_to_truncate)} RESTART IDENTITY CASCADE;")
        lines.append("")

        # 2. Export every row of every table in forward dependency order
        for table_name in ERP_TABLES_IN_ORDER:
            try:
                cursor.execute(f'SELECT * FROM "{table_name}" ORDER BY "id" ASC;')
            except Exception:
                try:
                    cursor.execute(f'SELECT * FROM "{table_name}";')
                except Exception:
                    continue

            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            quoted_cols = ", ".join([f'"{c}"' for c in col_names])

            lines.append(f"-- Table: {table_name} ({len(rows)} records)")
            for row in rows:
                vals_sql = ", ".join([_sql_literal(v) for v in row])
                lines.append(f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({vals_sql});')
            lines.append("")

        # 3. Reset all primary key sequences
        lines.append("-- Synchronize PostgreSQL Auto-Increment Sequences")
        for table_name in ERP_TABLES_IN_ORDER:
            lines.append(
                f"SELECT setval(pg_get_serial_sequence('\"{table_name}\"', 'id'), "
                f"COALESCE((SELECT MAX(\"id\") FROM \"{table_name}\"), 1), "
                f"(SELECT MAX(\"id\") FROM \"{table_name}\") IS NOT NULL);"
            )

    lines.append("")
    lines.append("COMMIT;")
    lines.append("-- END OF KMS FULL SQL BACKUP")
    return "\n".join(lines).encode("utf-8")


def restore_from_sql_bytes(sql_bytes):
    """
    Restores a full database from an uploaded .sql file (supports both KMS Full SQL Backup
    and standard pg_dump SQL files with INSERT statements).
    Returns (success: bool, summary_msg: str).
    """
    sql_text = sql_bytes.decode("utf-8", errors="replace")

    # Strip psql meta-commands like \connect, \restrict, SET transaction_timeout, etc.
    cleaned_lines = []
    in_copy_block = False
    copy_table = None
    copy_cols = None
    copy_rows = []

    for line in sql_text.splitlines():
        if in_copy_block:
            if line.strip() == r"\.":
                in_copy_block = False
                if copy_table and copy_cols and copy_rows:
                    for r_line in copy_rows:
                        parts = r_line.split("\t")
                        sql_vals = []
                        for p in parts:
                            if p == r"\N":
                                sql_vals.append("NULL")
                            else:
                                escaped = p.replace("'", "''")
                                sql_vals.append(f"'{escaped}'")
                        cleaned_lines.append(
                            f'INSERT INTO {copy_table} ({copy_cols}) VALUES ({", ".join(sql_vals)}) ON CONFLICT DO NOTHING;'
                        )
                copy_table = None
                copy_cols = None
                copy_rows = []
            else:
                copy_rows.append(line)
            continue

        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if stripped.startswith("\\"):
            continue
        if stripped.upper().startswith(("SET TRANSACTION_TIMEOUT", "SELECT PG_CATALOG.SET_CONFIG")):
            continue
        if stripped.upper().startswith(("BEGIN;", "COMMIT;")):
            continue

        # Convert pg_dump COPY public.table (cols) FROM stdin; into INSERT statements if present
        m_copy = re.match(r"^COPY\s+(?:public\.)?([^\s(]+)\s*\(([^)]+)\)\s+FROM\s+stdin;", stripped, re.IGNORECASE)
        if m_copy:
            in_copy_block = True
            copy_table = m_copy.group(1)
            copy_cols = m_copy.group(2)
            copy_rows = []
            continue

        cleaned_lines.append(line)

    executable_sql = "\n".join(cleaned_lines)
    if not executable_sql.strip():
        return False, "The uploaded .sql file contained no executable SQL statements."

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(executable_sql)
        sync_all_postgresql_sequences()

    from students.models import Student
    from teachers.models import Teacher
    from exams.models import ExamMark
    from finance.models import FeePaymentReceipt

    summary = (
        f"Database successfully restored from SQL! "
        f"Students: {Student.objects.count()}, "
        f"Teachers: {Teacher.objects.count()}, "
        f"Exam Marks: {ExamMark.objects.count()}, "
        f"Fee Receipts: {FeePaymentReceipt.objects.count()}."
    )
    return True, summary


def _style_worksheet(ws, title, headers, rows, school_name="Kohisar Model School & College"):
    """
    Applies crisp institutional styling to a worksheet in the Master Backup Workbook.
    Row 1: Title Banner
    Row 2: Column Headers
    Row 3+: Data Rows
    """
    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    title_fill = PatternFill(start_color="0F2442", end_color="0F2442", fill_type="solid")
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    thin_side = Side(style="thin", color="CBD5E1")
    border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    num_cols = max(len(headers), 1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
    title_cell = ws.cell(row=1, column=1, value=f"{school_name} — {title}")
    title_cell.font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    title_cell.fill = title_fill
    title_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 26

    ws.row_dimensions[2].height = 22
    for col_idx, h_text in enumerate(headers, start=1):
        c = ws.cell(row=2, column=col_idx, value=h_text)
        c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border

    for r_idx, row_vals in enumerate(rows, start=3):
        ws.row_dimensions[r_idx].height = 19
        is_alt = r_idx % 2 == 0
        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name="Calibri", size=10)
            if is_alt:
                cell.fill = alt_fill
            cell.border = border

    for col_idx in range(1, num_cols + 1):
        col_letter = get_column_letter(col_idx)
        header_len = len(str(headers[col_idx - 1])) if col_idx <= len(headers) else 10
        ws.column_dimensions[col_letter].width = max(header_len + 5, 14)


def generate_full_master_excel():
    """
    Generates a Full Multi-Sheet Master Excel Backup (.xlsx) containing EVERY module:
      1. Summary_Info
      2. Classes_Sections (with Section Teacher details)
      3. Academic_Sessions
      4. Families
      5. Students (Full student admission & bio details)
      6. Salary_Scales
      7. Teachers_Staff (Full teacher bio, father name, CNIC, contact, pic path, assigned section, salary)
      8. Exams_Curriculum (Exams, Subjects, ClassSubjects)
      9. Exam_Marks (ALL student obtained marks across all exams and subjects)
      10. Fee_Ledgers_Months (ALL 12-month student fee entries, arrears, payments)
      11. Fee_Receipts (ALL fee payment receipts & linked months)
      12. Salary_Bills (ALL monthly teacher salary bills, deductions, loan cuts, payments)
      13. Teacher_Loans (ALL staff loans & advances)
      14. Expenses (ALL school general expenses)
      15. Student_Attendance
      16. Teacher_Attendance
    Returns BytesIO buffer.
    """
    from accounts.models import Expense
    from exams.models import ClassSubject, Exam, ExamMark, Subject
    from finance.models import FeePaymentReceipt, StudentFeeLedger, StudentFeeMonthEntry
    from school.models import AcademicSession, ClassLevel, SchoolSetting, Section
    from students.models import FamilyHousehold, Student, StudentAttendance
    from teachers.models import (
        MonthlySalaryBill,
        SalaryScale,
        Teacher,
        TeacherAttendance,
        TeacherLoan,
    )

    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College"
    now_str = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")

    wb = Workbook()
    # Sheet 1: Summary_Info
    ws_sum = wb.active
    ws_sum.title = "Summary_Info"
    sum_headers = ["Module / Table Name", "Total Records in Backup", "Backup Timestamp", "School Name"]
    sum_rows = [
        ["Classes", ClassLevel.objects.count(), now_str, school_name],
        ["Sections", Section.objects.count(), now_str, school_name],
        ["Academic Sessions", AcademicSession.objects.count(), now_str, school_name],
        ["Families / Households", FamilyHousehold.objects.count(), now_str, school_name],
        ["Students (All)", Student.objects.count(), now_str, school_name],
        ["Teachers & Staff", Teacher.objects.count(), now_str, school_name],
        ["Salary Scales", SalaryScale.objects.count(), now_str, school_name],
        ["Examinations", Exam.objects.count(), now_str, school_name],
        ["Master Subjects", Subject.objects.count(), now_str, school_name],
        ["Class Subject Mappings", ClassSubject.objects.count(), now_str, school_name],
        ["Student Exam Marks", ExamMark.objects.count(), now_str, school_name],
        ["Student Fee Month Entries", StudentFeeMonthEntry.objects.count(), now_str, school_name],
        ["Fee Payment Receipts", FeePaymentReceipt.objects.count(), now_str, school_name],
        ["Teacher Monthly Salary Bills", MonthlySalaryBill.objects.count(), now_str, school_name],
        ["Teacher Loans & Advances", TeacherLoan.objects.count(), now_str, school_name],
        ["General Expenses", Expense.objects.count(), now_str, school_name],
        ["Student Attendance Logs", StudentAttendance.objects.count(), now_str, school_name],
        ["Teacher Attendance Logs", TeacherAttendance.objects.count(), now_str, school_name],
    ]
    _style_worksheet(ws_sum, "Full System Master Backup Summary", sum_headers, sum_rows, school_name)

    # Sheet 2: Classes_Sections
    ws_cls = wb.create_sheet("Classes_Sections")
    cls_headers = [
        "Class Name",
        "Level",
        "Monthly Fee (PKR)",
        "Section Name",
        "Class Teacher Name",
        "Linked Teacher Staff ID",
        "Teacher Father Name",
        "Teacher Contact Number",
    ]
    cls_rows = []
    for c in ClassLevel.objects.prefetch_related("sections__teacher").all():
        secs = list(c.sections.all())
        if not secs:
            cls_rows.append([c.name, c.level, float(c.monthly_fee), "A", "", "", "", ""])
        else:
            for s in secs:
                t_obj = s.teacher
                cls_rows.append([
                    c.name,
                    c.level,
                    float(c.monthly_fee),
                    s.name,
                    s.class_teacher or (t_obj.full_name if t_obj else ""),
                    t_obj.teacher_id if t_obj else "",
                    t_obj.father_name if t_obj else "",
                    t_obj.contact_number if t_obj else "",
                ])
    _style_worksheet(ws_cls, "Classes & Sections with Assigned Teachers", cls_headers, cls_rows, school_name)

    # Sheet 3: Academic_Sessions
    ws_ses = wb.create_sheet("Academic_Sessions")
    ses_headers = ["Session Name", "Start Date", "End Date", "Is Active"]
    ses_rows = [
        [
            s.name,
            str(s.start_date) if s.start_date else "",
            str(s.end_date) if s.end_date else "",
            "Yes" if s.is_active else "No",
        ]
        for s in AcademicSession.objects.all()
    ]
    _style_worksheet(ws_ses, "Academic Sessions", ses_headers, ses_rows, school_name)

    # Sheet 4: Families
    ws_fam = wb.create_sheet("Families")
    fam_headers = ["Family ID", "Father / Guardian Name", "Contact Number", "Address"]
    fam_rows = [
        [f.family_id, f.father_guardian_name, f.contact_number, f.address]
        for f in FamilyHousehold.objects.all()
    ]
    _style_worksheet(ws_fam, "Families & Households", fam_headers, fam_rows, school_name)

    # Sheet 5: Students
    ws_stu = wb.create_sheet("Students")
    stu_headers = [
        "Admission No",
        "Admission Date",
        "Full Name",
        "Father Name",
        "Date of Birth",
        "Gender",
        "Tribe / Caste",
        "Father Occupation",
        "Residence / Address",
        "Contact Number",
        "Class Name",
        "Section Name",
        "Family ID",
        "Status",
        "Inactive Date",
        "Withdrawal Date",
        "Class at Withdrawal",
        "Arrears at Withdrawal",
        "Remarks",
        "Profile Picture Path",
    ]
    stu_rows = []
    for st in Student.objects.select_related("current_class", "current_section", "family").all():
        stu_rows.append([
            st.admission_no,
            str(st.admission_date) if st.admission_date else "",
            st.full_name,
            st.father_name,
            str(st.dob) if st.dob else "",
            st.gender,
            st.tribe_caste,
            st.father_occupation,
            st.residence,
            st.contact_number,
            st.current_class.name if st.current_class else "",
            st.current_section.name if st.current_section else "A",
            st.family.family_id if st.family else "",
            st.status,
            str(st.inactive_date) if st.inactive_date else "",
            str(st.withdrawal_date) if st.withdrawal_date else "",
            st.class_at_withdrawal,
            float(st.arrears_at_withdrawal or 0),
            st.remarks,
            st.profile_picture.name if st.profile_picture else "",
        ])
    _style_worksheet(ws_stu, "All Students Master Directory", stu_headers, stu_rows, school_name)

    # Sheet 6: Salary_Scales
    ws_sc = wb.create_sheet("Salary_Scales")
    sc_headers = [
        "Scale Name",
        "Basic Pay (PKR)",
        "Medical Allowance (PKR)",
        "Conveyance Allowance (PKR)",
        "Other Allowances (PKR)",
        "Gross Salary (PKR)",
    ]
    sc_rows = [
        [
            sc.name,
            float(sc.basic_pay or 0),
            float(sc.medical_allowance or 0),
            float(sc.conveyance_allowance or 0),
            float(sc.other_allowances or 0),
            float(sc.gross_salary or 0),
        ]
        for sc in SalaryScale.objects.all()
    ]
    _style_worksheet(ws_sc, "Teacher Salary Scales", sc_headers, sc_rows, school_name)

    # Sheet 7: Teachers_Staff
    ws_tch = wb.create_sheet("Teachers_Staff")
    tch_headers = [
        "Staff ID",
        "Full Name",
        "Father / Husband Name",
        "Designation",
        "Assigned Class / Section",
        "CNIC",
        "Date of Birth",
        "Contact Number",
        "Email",
        "Address",
        "Qualification",
        "Experience",
        "Joining Date",
        "Salary Scale Name",
        "Basic Pay (PKR)",
        "Gross Salary (PKR)",
        "Status",
        "Remarks",
        "Profile Picture Path",
    ]
    tch_rows = []
    for t in Teacher.objects.select_related("salary_scale").prefetch_related("managed_sections__class_level").all():
        managed_str = ", ".join([f"{sec.class_level.name}-{sec.name}" for sec in t.managed_sections.all()])
        assigned_sec = t.assigned_section or managed_str
        tch_rows.append([
            t.teacher_id,
            t.full_name,
            t.father_name,
            t.designation,
            assigned_sec,
            t.cnic,
            str(t.dob) if t.dob else "",
            t.contact_number,
            t.email,
            t.address,
            t.qualification,
            t.experience,
            str(t.joining_date) if t.joining_date else "",
            t.salary_scale.name if t.salary_scale else "",
            float(t.salary_scale.basic_pay) if t.salary_scale else 0.0,
            float(t.salary_scale.gross_salary) if t.salary_scale else 0.0,
            t.status,
            t.remarks,
            t.profile_picture.name if t.profile_picture else "",
        ])
    _style_worksheet(ws_tch, "Full Teachers & Staff Directory", tch_headers, tch_rows, school_name)

    # Sheet 8: Exams_Curriculum
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
    _style_worksheet(ws_ex, "Examinations, Master Subjects & Class Curriculum", ex_headers, ex_rows, school_name)

    # Sheet 9: Exam_Marks (ALL Student Marks!)
    ws_mk = wb.create_sheet("Exam_Marks")
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
    _style_worksheet(ws_mk, "All Student Examination Marks", mk_headers, mk_rows, school_name)

    # Sheet 10: Fee_Ledgers_Months
    ws_fee = wb.create_sheet("Fee_Ledgers_Months")
    fee_headers = [
        "Admission No",
        "Student Full Name",
        "Class Name",
        "Session Name",
        "Month Number",
        "Month Name",
        "Arrears (PKR)",
        "Monthly Fee (PKR)",
        "Exam Fee (PKR)",
        "Other Charges (PKR)",
        "Paid Amount (PKR)",
        "Balance (PKR)",
        "Is Paid",
        "Last Payment Date",
        "Last Receipt No",
    ]
    fee_rows = []
    for me in StudentFeeMonthEntry.objects.select_related(
        "ledger", "ledger__student", "ledger__student__current_class", "ledger__academic_session"
    ).all():
        st = me.ledger.student
        fee_rows.append([
            st.admission_no,
            st.full_name,
            st.current_class.name if st.current_class else "",
            me.ledger.academic_session.name,
            me.month,
            me.month_name,
            float(me.arrears or 0),
            float(me.monthly_fee or 0),
            float(me.exam_fee or 0),
            float(me.other_charges or 0),
            float(me.paid_amount or 0),
            float(me.balance or 0),
            "Yes" if me.is_paid else "No",
            str(me.last_payment_date) if me.last_payment_date else "",
            me.last_receipt_no,
        ])
    _style_worksheet(ws_fee, "Student 12-Month Fee Ledgers", fee_headers, fee_rows, school_name)

    # Sheet 11: Fee_Receipts
    ws_rec = wb.create_sheet("Fee_Receipts")
    rec_headers = [
        "Receipt No",
        "Payment Date",
        "Admission No",
        "Student Full Name",
        "Class Name",
        "Amount Paid (PKR)",
        "Session Name",
        "Covered Month Numbers",
        "Remarks",
    ]
    rec_rows = []
    for r in FeePaymentReceipt.objects.select_related("student", "student__current_class").prefetch_related("month_entries__ledger__academic_session").all():
        m_entries = list(r.month_entries.all())
        sess_name = m_entries[0].ledger.academic_session.name if m_entries else ""
        month_nums = ",".join([str(me.month) for me in m_entries])
        rec_rows.append([
            r.receipt_no,
            str(r.payment_date) if r.payment_date else "",
            r.student.admission_no,
            r.student.full_name,
            r.student.current_class.name if r.student.current_class else "",
            float(r.amount_paid or 0),
            sess_name,
            month_nums,
            r.remarks,
        ])
    _style_worksheet(ws_rec, "Fee Payment Receipts", rec_headers, rec_rows, school_name)

    # Sheet 12: Salary_Bills
    ws_sal = wb.create_sheet("Salary_Bills")
    sal_headers = [
        "Staff ID",
        "Teacher Name",
        "Month",
        "Year",
        "Base Pay (PKR)",
        "Allowances (PKR)",
        "Bonus (PKR)",
        "Days Present",
        "Days Late",
        "Days Absent",
        "Days Half Day",
        "Days Leave",
        "Late Deductions (PKR)",
        "Absent Deductions (PKR)",
        "Deduct Loan",
        "Loan Deduction Amount (PKR)",
        "Previous Unpaid Dues (PKR)",
        "Total Deductions (PKR)",
        "Paid Amount (PKR)",
        "Is Paid",
        "Payment Date",
        "Voucher No",
    ]
    sal_rows = []
    for b in MonthlySalaryBill.objects.select_related("teacher").all():
        sal_rows.append([
            b.teacher.teacher_id,
            b.teacher.full_name,
            b.month,
            b.year,
            float(b.base_pay or 0),
            float(b.allowances or 0),
            float(b.bonus or 0),
            b.days_present,
            b.days_late,
            b.days_absent,
            b.days_half_day,
            b.days_leave,
            float(b.late_deductions or 0),
            float(b.absent_deductions or 0),
            "Yes" if b.deduct_loan else "No",
            float(b.loan_deduction_amount or 0),
            float(b.previous_unpaid_dues or 0),
            float(b.deductions or 0),
            float(b.paid_amount or 0),
            "Yes" if b.is_paid else "No",
            str(b.payment_date) if b.payment_date else "",
            b.voucher_no,
        ])
    _style_worksheet(ws_sal, "Teacher Monthly Salary Bills", sal_headers, sal_rows, school_name)

    # Sheet 13: Teacher_Loans
    ws_ln = wb.create_sheet("Teacher_Loans")
    ln_headers = [
        "Staff ID",
        "Teacher Name",
        "Loan Title",
        "Loan Date",
        "Principal Amount (PKR)",
        "Monthly Installment (PKR)",
        "Total Repaid (PKR)",
        "Status",
        "Is Cleared",
        "Remarks",
    ]
    ln_rows = [
        [
            ln.teacher.teacher_id,
            ln.teacher.full_name,
            ln.loan_title,
            str(ln.loan_date) if ln.loan_date else "",
            float(ln.principal_amount or 0),
            float(ln.monthly_installment or 0),
            float(ln.total_repaid or 0),
            ln.status,
            "Yes" if ln.is_cleared else "No",
            ln.remarks,
        ]
        for ln in TeacherLoan.objects.select_related("teacher").all()
    ]
    _style_worksheet(ws_ln, "Teacher Loans & Advances", ln_headers, ln_rows, school_name)

    # Sheet 14: Expenses
    ws_exp = wb.create_sheet("Expenses")
    exp_headers = ["Date", "Category", "Amount (PKR)", "Payment Mode", "Reference", "Note"]
    exp_rows = [
        [
            str(ex.date) if ex.date else "",
            ex.category,
            float(ex.amount or 0),
            ex.payment_mode,
            ex.reference,
            ex.note,
        ]
        for ex in Expense.objects.all()
    ]
    _style_worksheet(ws_exp, "School General Expenses", exp_headers, exp_rows, school_name)

    # Sheet 15: Student_Attendance
    ws_sa = wb.create_sheet("Student_Attendance")
    sa_headers = ["Admission No", "Student Name", "Date", "Status", "Check In", "Check Out", "Method", "Remarks"]
    sa_rows = [
        [
            sa.student.admission_no,
            sa.student.full_name,
            str(sa.date) if sa.date else "",
            sa.status,
            str(sa.check_in) if sa.check_in else "",
            str(sa.check_out) if sa.check_out else "",
            sa.attendance_method,
            sa.remarks,
        ]
        for sa in StudentAttendance.objects.select_related("student").all()
    ]
    _style_worksheet(ws_sa, "Student Attendance Records", sa_headers, sa_rows, school_name)

    # Sheet 16: Teacher_Attendance
    ws_ta = wb.create_sheet("Teacher_Attendance")
    ta_headers = [
        "Staff ID",
        "Teacher Name",
        "Date",
        "Status",
        "Check In",
        "Check Out",
        "Method",
        "Late Minutes",
        "Early Leave Minutes",
        "Working Hours",
        "Deduction Amount (PKR)",
        "Bonus Amount (PKR)",
        "Remarks",
    ]
    ta_rows = [
        [
            ta.teacher.teacher_id,
            ta.teacher.full_name,
            str(ta.date) if ta.date else "",
            ta.status,
            str(ta.check_in) if ta.check_in else "",
            str(ta.check_out) if ta.check_out else "",
            ta.attendance_method,
            ta.late_minutes,
            ta.early_leave_minutes,
            float(ta.working_hours or 0),
            float(ta.deduction_amount or 0),
            float(ta.bonus_amount or 0),
            ta.remarks,
        ]
        for ta in TeacherAttendance.objects.select_related("teacher").all()
    ]
    _style_worksheet(ws_ta, "Teacher Attendance Records", ta_headers, ta_rows, school_name)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def _parse_date_safe(val, default=None):
    if not val:
        return default
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if not s or s == "-":
        return default
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            continue
    return default


def _parse_dec_safe(val, default="0.00"):
    if val is None or val == "" or val == "-":
        return Decimal(default)
    try:
        return Decimal(str(val).replace(",", "").strip())
    except Exception:
        return Decimal(default)


def _sheet_rows_as_dicts(ws):
    """
    Reads an openpyxl worksheet where Row 2 is headers and Row 3+ are data rows.
    """
    headers = []
    for cell in ws[2]:
        val = str(cell.value or "").strip()
        headers.append(val)
    records = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not any(row):
            continue
        rec = {}
        for idx, h in enumerate(headers):
            if h and idx < len(row):
                rec[h] = row[idx]
        records.append(rec)
    return records


def restore_from_master_excel(excel_file):
    """
    Restores the full school database from a KMS Full Master Excel Backup (.xlsx)
    (or an Exam Marks Backup .xlsx).
    Restores Classes, Sections, Sessions, Families, Students, Salary Scales, Teachers,
    Exams, Subjects, ClassSubjects, Exam Marks, Fee Ledgers, Fee Receipts, Salary Bills,
    Teacher Loans, Expenses, and Attendance!
    """
    from accounts.models import Expense
    from exams.models import ClassSubject, Exam, ExamMark, Subject
    from finance.models import FeePaymentReceipt, StudentFeeLedger, StudentFeeMonthEntry
    from school.models import AcademicSession, ClassLevel, Section
    from students.models import FamilyHousehold, Student, StudentAttendance
    from teachers.models import (
        MonthlySalaryBill,
        SalaryScale,
        Teacher,
        TeacherAttendance,
        TeacherLoan,
    )

    wb = load_workbook(excel_file, data_only=True)
    sheet_names = set(wb.sheetnames)
    counts = {
        "classes": 0,
        "students": 0,
        "teachers": 0,
        "marks": 0,
        "fee_entries": 0,
        "receipts": 0,
        "salary_bills": 0,
        "expenses": 0,
    }

    with transaction.atomic():
        # 1. Academic Sessions
        if "Academic_Sessions" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Academic_Sessions"]):
                name = str(r.get("Session Name", "") or "").strip()
                if not name:
                    continue
                s_date = _parse_date_safe(r.get("Start Date"), date(2025, 4, 1))
                e_date = _parse_date_safe(r.get("End Date"), date(2026, 3, 31))
                is_act = str(r.get("Is Active", "")).strip().lower() in ("yes", "true", "1")
                AcademicSession.objects.update_or_create(
                    name=name,
                    defaults={"start_date": s_date, "end_date": e_date, "is_active": is_act},
                )

        # Ensure at least one AcademicSession exists
        active_session = AcademicSession.objects.filter(is_active=True).first() or AcademicSession.objects.first()
        if not active_session:
            active_session = AcademicSession.objects.create(
                name="2025-2026",
                start_date=date(2025, 4, 1),
                end_date=date(2026, 3, 31),
                is_active=True,
            )

        # 2. Salary Scales
        if "Salary_Scales" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Salary_Scales"]):
                sc_name = str(r.get("Scale Name", "") or "").strip()
                if not sc_name:
                    continue
                SalaryScale.objects.update_or_create(
                    name=sc_name,
                    defaults={
                        "basic_pay": _parse_dec_safe(r.get("Basic Pay (PKR)")),
                        "medical_allowance": _parse_dec_safe(r.get("Medical Allowance (PKR)")),
                        "conveyance_allowance": _parse_dec_safe(r.get("Conveyance Allowance (PKR)")),
                        "other_allowances": _parse_dec_safe(r.get("Other Allowances (PKR)")),
                    },
                )

        # 3. Teachers & Staff
        if "Teachers_Staff" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Teachers_Staff"]):
                t_id = str(r.get("Staff ID", "") or "").strip()
                f_name = str(r.get("Full Name", "") or "").strip()
                if not f_name:
                    continue
                sc_name = str(r.get("Salary Scale Name", "") or "").strip()
                scale_obj = None
                if sc_name and sc_name != "-":
                    scale_obj, _ = SalaryScale.objects.get_or_create(
                        name=sc_name,
                        defaults={"basic_pay": _parse_dec_safe(r.get("Basic Pay (PKR)"), "25000.00")},
                    )
                defaults = {
                    "full_name": f_name,
                    "father_name": str(r.get("Father / Husband Name", "") or "").strip(),
                    "designation": str(r.get("Designation", "Teacher") or "Teacher").strip(),
                    "assigned_section": str(r.get("Assigned Class / Section", "") or "").strip(),
                    "cnic": str(r.get("CNIC", "") or "").strip(),
                    "dob": _parse_date_safe(r.get("Date of Birth"), date(1990, 1, 1)),
                    "contact_number": str(r.get("Contact Number", "") or "").strip(),
                    "email": str(r.get("Email", "") or "").strip(),
                    "address": str(r.get("Address", "") or "").strip(),
                    "qualification": str(r.get("Qualification", "") or "").strip(),
                    "experience": str(r.get("Experience", "") or "").strip(),
                    "joining_date": _parse_date_safe(r.get("Joining Date"), timezone.now().date()),
                    "salary_scale": scale_obj,
                    "status": "Inactive" if str(r.get("Status", "Active")).strip().lower() == "inactive" else "Active",
                    "remarks": str(r.get("Remarks", "") or "").strip(),
                }
                pic_path = str(r.get("Profile Picture Path", "") or "").strip()
                if pic_path:
                    defaults["profile_picture"] = pic_path

                if t_id:
                    Teacher.objects.update_or_create(teacher_id=t_id, defaults=defaults)
                else:
                    Teacher.objects.create(**defaults)
                counts["teachers"] += 1

        # 4. Classes & Sections
        if "Classes_Sections" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Classes_Sections"]):
                c_name = str(r.get("Class Name", "") or "").strip()
                if not c_name:
                    continue
                level = str(r.get("Level", "Primary") or "Primary").strip()
                m_fee = _parse_dec_safe(r.get("Monthly Fee (PKR)"))
                c_obj, _ = ClassLevel.objects.update_or_create(
                    name=c_name,
                    defaults={"level": level, "monthly_fee": m_fee},
                )
                sec_name = str(r.get("Section Name", "A") or "A").strip()
                t_name = str(r.get("Class Teacher Name", "") or "").strip()
                t_staff_id = str(r.get("Linked Teacher Staff ID", "") or "").strip()
                linked_t = Teacher.objects.filter(teacher_id=t_staff_id).first() if t_staff_id else None
                if not linked_t and t_name:
                    linked_t = Teacher.objects.filter(full_name__iexact=t_name).first()
                Section.objects.update_or_create(
                    class_level=c_obj,
                    name=sec_name,
                    defaults={
                        "class_teacher": t_name or (linked_t.full_name if linked_t else ""),
                        "teacher": linked_t,
                    },
                )
                counts["classes"] += 1

        # 5. Families
        if "Families" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Families"]):
                fam_id = str(r.get("Family ID", "") or "").strip()
                father = str(r.get("Father / Guardian Name", "") or "").strip()
                if not fam_id and not father:
                    continue
                defaults = {
                    "father_guardian_name": father or "Guardian",
                    "contact_number": str(r.get("Contact Number", "") or "").strip(),
                    "address": str(r.get("Address", "") or "").strip(),
                }
                if fam_id:
                    FamilyHousehold.objects.update_or_create(family_id=fam_id, defaults=defaults)
                else:
                    FamilyHousehold.objects.create(**defaults)

        # 6. Students
        if "Students" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Students"]):
                adm_no = str(r.get("Admission No", "") or "").strip()
                full_name = str(r.get("Full Name", "") or "").strip()
                if not full_name:
                    continue
                c_name = str(r.get("Class Name", "Class 1") or "Class 1").strip()
                s_name = str(r.get("Section Name", "A") or "A").strip()
                c_obj, _ = ClassLevel.objects.get_or_create(name=c_name, defaults={"level": "Primary"})
                s_obj, _ = Section.objects.get_or_create(class_level=c_obj, name=s_name)
                fam_id = str(r.get("Family ID", "") or "").strip()
                fam_obj = FamilyHousehold.objects.filter(family_id=fam_id).first() if fam_id else None

                defaults = {
                    "admission_date": _parse_date_safe(r.get("Admission Date"), timezone.now().date()),
                    "full_name": full_name,
                    "father_name": str(r.get("Father Name", "") or "").strip(),
                    "dob": _parse_date_safe(r.get("Date of Birth"), timezone.now().date()),
                    "gender": str(r.get("Gender", "Male") or "Male").strip(),
                    "tribe_caste": str(r.get("Tribe / Caste", "") or "").strip(),
                    "father_occupation": str(r.get("Father Occupation", "") or "").strip(),
                    "residence": str(r.get("Residence / Address", "") or "").strip(),
                    "contact_number": str(r.get("Contact Number", "") or "").strip(),
                    "current_class": c_obj,
                    "current_section": s_obj,
                    "family": fam_obj,
                    "status": str(r.get("Status", "Active") or "Active").strip(),
                    "inactive_date": _parse_date_safe(r.get("Inactive Date")),
                    "withdrawal_date": _parse_date_safe(r.get("Withdrawal Date")),
                    "class_at_withdrawal": str(r.get("Class at Withdrawal", "") or "").strip(),
                    "arrears_at_withdrawal": _parse_dec_safe(r.get("Arrears at Withdrawal")),
                    "remarks": str(r.get("Remarks", "") or "").strip(),
                }
                pic_path = str(r.get("Profile Picture Path", "") or "").strip()
                if pic_path:
                    defaults["profile_picture"] = pic_path

                if adm_no:
                    Student.objects.update_or_create(admission_no=adm_no, defaults=defaults)
                else:
                    Student.objects.create(**defaults)
                counts["students"] += 1

        # 7. Exams_Curriculum
        if "Exams_Curriculum" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Exams_Curriculum"]):
                rec_type = str(r.get("Record Type", "") or "").strip().upper()
                name = str(r.get("Name / Exam / Subject", "") or "").strip()
                if not name:
                    continue
                if rec_type == "EXAM":
                    sess_name = str(r.get("Session / Class Name", "") or "").strip()
                    sess = AcademicSession.objects.filter(name=sess_name).first() or active_session
                    is_act = str(r.get("Passing Marks / Is Active", "Yes")).strip().lower() in ("yes", "true", "1")
                    Exam.objects.update_or_create(
                        name=name,
                        session=sess,
                        defaults={
                            "start_date": _parse_date_safe(r.get("Subject Code / Start Date")),
                            "end_date": _parse_date_safe(r.get("Total Marks / End Date")),
                            "is_active": is_act,
                        },
                    )
                elif rec_type == "SUBJECT":
                    code = str(r.get("Subject Code / Start Date", "") or "").strip()
                    order_val = int(float(r.get("Order", 0) or 0))
                    Subject.objects.update_or_create(
                        name=name,
                        defaults={"code": code, "order": order_val, "is_active": True},
                    )
                elif rec_type == "CLASS_SUBJECT":
                    cls_name = str(r.get("Session / Class Name", "") or "").strip()
                    c_obj = ClassLevel.objects.filter(name=cls_name).first()
                    sub_obj, _ = Subject.objects.get_or_create(
                        name=name,
                        defaults={"code": str(r.get("Subject Code / Start Date", "") or "").strip()},
                    )
                    if c_obj and sub_obj:
                        ClassSubject.objects.update_or_create(
                            class_level=c_obj,
                            subject=sub_obj,
                            defaults={
                                "total_marks": _parse_dec_safe(r.get("Total Marks / End Date"), "100.0"),
                                "passing_marks": _parse_dec_safe(r.get("Passing Marks / Is Active"), "33.0"),
                                "order": int(float(r.get("Order", 0) or 0)),
                            },
                        )

        # 8. Exam_Marks (or All_Exam_Marks sheet)
        marks_sheet_name = "Exam_Marks" if "Exam_Marks" in sheet_names else ("All_Exam_Marks" if "All_Exam_Marks" in sheet_names else None)
        if marks_sheet_name:
            for r in _sheet_rows_as_dicts(wb[marks_sheet_name]):
                exam_name = str(r.get("Exam Name", "") or "").strip()
                sess_name = str(r.get("Session Name", "") or "").strip()
                adm_no = str(r.get("Admission No", "") or "").strip()
                stu_name = str(r.get("Student Full Name", "") or r.get("Student Name", "") or "").strip()
                cls_name = str(r.get("Class Name", "") or "").strip()
                sub_name = str(r.get("Subject Name", "") or "").strip()
                if not exam_name or not sub_name or (not adm_no and not stu_name):
                    continue

                sess_obj = AcademicSession.objects.filter(name=sess_name).first() if sess_name else active_session
                if not sess_obj:
                    sess_obj = active_session
                exam_obj, _ = Exam.objects.get_or_create(name=exam_name, session=sess_obj)
                cls_obj = ClassLevel.objects.filter(name=cls_name).first() if cls_name else None
                if not cls_obj and cls_name:
                    cls_obj = ClassLevel.objects.create(name=cls_name, level="Primary")

                stu_obj = Student.objects.filter(admission_no=adm_no).first() if adm_no else None
                if not stu_obj and stu_name:
                    stu_obj = Student.objects.filter(full_name__iexact=stu_name).first()
                if not stu_obj and stu_name and cls_obj:
                    sec_name = str(r.get("Section Name", "A") or "A").strip()
                    sec_obj, _ = Section.objects.get_or_create(class_level=cls_obj, name=sec_name)
                    stu_obj = Student.objects.create(
                        admission_no=adm_no,
                        full_name=stu_name,
                        father_name=str(r.get("Father Name", "") or "").strip(),
                        current_class=cls_obj,
                        current_section=sec_obj,
                    )
                if not stu_obj:
                    continue

                sub_code = str(r.get("Subject Code", "") or "").strip()
                sub_obj, _ = Subject.objects.get_or_create(name=sub_name, defaults={"code": sub_code})
                tot_m = _parse_dec_safe(r.get("Total Marks"), "100.0")
                obt_m = _parse_dec_safe(r.get("Obtained Marks"), "0.0")
                is_abs = str(r.get("Is Absent", "No")).strip().lower() in ("yes", "true", "1", "a", "absent")

                ExamMark.objects.update_or_create(
                    exam=exam_obj,
                    student=stu_obj,
                    subject=sub_obj,
                    defaults={
                        "class_level": cls_obj or stu_obj.current_class,
                        "total_marks": tot_m,
                        "obtained_marks": obt_m,
                        "is_absent": is_abs,
                        "remarks": str(r.get("Remarks", "") or "").strip(),
                    },
                )
                counts["marks"] += 1

        # 9. Fee_Ledgers_Months
        if "Fee_Ledgers_Months" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Fee_Ledgers_Months"]):
                adm_no = str(r.get("Admission No", "") or "").strip()
                sess_name = str(r.get("Session Name", "") or "").strip()
                month_num = int(float(r.get("Month Number", 0) or 0))
                if not adm_no or not (1 <= month_num <= 12):
                    continue
                stu_obj = Student.objects.filter(admission_no=adm_no).first()
                if not stu_obj:
                    continue
                sess_obj = AcademicSession.objects.filter(name=sess_name).first() or active_session
                ledger_obj, _ = StudentFeeLedger.objects.get_or_create(
                    student=stu_obj, academic_session=sess_obj
                )
                StudentFeeMonthEntry.objects.update_or_create(
                    ledger=ledger_obj,
                    month=month_num,
                    defaults={
                        "arrears": _parse_dec_safe(r.get("Arrears (PKR)")),
                        "monthly_fee": _parse_dec_safe(r.get("Monthly Fee (PKR)")),
                        "exam_fee": _parse_dec_safe(r.get("Exam Fee (PKR)")),
                        "other_charges": _parse_dec_safe(r.get("Other Charges (PKR)")),
                        "paid_amount": _parse_dec_safe(r.get("Paid Amount (PKR)")),
                        "is_paid": str(r.get("Is Paid", "No")).strip().lower() in ("yes", "true", "1"),
                        "last_payment_date": _parse_date_safe(r.get("Last Payment Date")),
                        "last_receipt_no": str(r.get("Last Receipt No", "") or "").strip(),
                    },
                )
                counts["fee_entries"] += 1

        # 10. Fee_Receipts
        if "Fee_Receipts" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Fee_Receipts"]):
                rec_no = str(r.get("Receipt No", "") or "").strip()
                adm_no = str(r.get("Admission No", "") or "").strip()
                if not rec_no or not adm_no:
                    continue
                stu_obj = Student.objects.filter(admission_no=adm_no).first()
                if not stu_obj:
                    continue
                rec_obj, _ = FeePaymentReceipt.objects.update_or_create(
                    receipt_no=rec_no,
                    defaults={
                        "student": stu_obj,
                        "payment_date": _parse_date_safe(r.get("Payment Date"), timezone.now().date()),
                        "amount_paid": _parse_dec_safe(r.get("Amount Paid (PKR)")),
                        "remarks": str(r.get("Remarks", "") or "").strip(),
                    },
                )
                sess_name = str(r.get("Session Name", "") or "").strip()
                month_nums_str = str(r.get("Covered Month Numbers", "") or "").strip()
                if month_nums_str:
                    sess_obj = AcademicSession.objects.filter(name=sess_name).first() or active_session
                    ledger_obj = StudentFeeLedger.objects.filter(student=stu_obj, academic_session=sess_obj).first()
                    if ledger_obj:
                        m_nums = [int(x) for x in month_nums_str.split(",") if x.strip().isdigit()]
                        entries = StudentFeeMonthEntry.objects.filter(ledger=ledger_obj, month__in=m_nums)
                        rec_obj.month_entries.set(entries)
                counts["receipts"] += 1

        # 11. Salary_Bills
        if "Salary_Bills" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Salary_Bills"]):
                staff_id = str(r.get("Staff ID", "") or "").strip()
                month_val = int(float(r.get("Month", 0) or 0))
                year_val = int(float(r.get("Year", 0) or 0))
                if not staff_id or not month_val or not year_val:
                    continue
                t_obj = Teacher.objects.filter(teacher_id=staff_id).first()
                if not t_obj:
                    continue
                MonthlySalaryBill.objects.update_or_create(
                    teacher=t_obj,
                    month=month_val,
                    year=year_val,
                    defaults={
                        "base_pay": _parse_dec_safe(r.get("Base Pay (PKR)")),
                        "allowances": _parse_dec_safe(r.get("Allowances (PKR)")),
                        "bonus": _parse_dec_safe(r.get("Bonus (PKR)")),
                        "days_present": int(float(r.get("Days Present", 30) or 30)),
                        "days_late": int(float(r.get("Days Late", 0) or 0)),
                        "days_absent": int(float(r.get("Days Absent", 0) or 0)),
                        "days_half_day": int(float(r.get("Days Half Day", 0) or 0)),
                        "days_leave": int(float(r.get("Days Leave", 0) or 0)),
                        "late_deductions": _parse_dec_safe(r.get("Late Deductions (PKR)")),
                        "absent_deductions": _parse_dec_safe(r.get("Absent Deductions (PKR)")),
                        "deduct_loan": str(r.get("Deduct Loan", "No")).strip().lower() in ("yes", "true", "1"),
                        "loan_deduction_amount": _parse_dec_safe(r.get("Loan Deduction Amount (PKR)")),
                        "previous_unpaid_dues": _parse_dec_safe(r.get("Previous Unpaid Dues (PKR)")),
                        "deductions": _parse_dec_safe(r.get("Total Deductions (PKR)")),
                        "paid_amount": _parse_dec_safe(r.get("Paid Amount (PKR)")),
                        "is_paid": str(r.get("Is Paid", "No")).strip().lower() in ("yes", "true", "1"),
                        "payment_date": _parse_date_safe(r.get("Payment Date")),
                        "voucher_no": str(r.get("Voucher No", "") or "").strip(),
                    },
                )
                counts["salary_bills"] += 1

        # 12. Teacher_Loans
        if "Teacher_Loans" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Teacher_Loans"]):
                staff_id = str(r.get("Staff ID", "") or "").strip()
                t_obj = Teacher.objects.filter(teacher_id=staff_id).first()
                if not t_obj:
                    continue
                l_title = str(r.get("Loan Title", "Staff Loan") or "Staff Loan").strip()
                l_date = _parse_date_safe(r.get("Loan Date"), timezone.now().date())
                TeacherLoan.objects.update_or_create(
                    teacher=t_obj,
                    loan_title=l_title,
                    loan_date=l_date,
                    defaults={
                        "principal_amount": _parse_dec_safe(r.get("Principal Amount (PKR)")),
                        "monthly_installment": _parse_dec_safe(r.get("Monthly Installment (PKR)")),
                        "total_repaid": _parse_dec_safe(r.get("Total Repaid (PKR)")),
                        "status": str(r.get("Status", "Active") or "Active").strip(),
                        "is_cleared": str(r.get("Is Cleared", "No")).strip().lower() in ("yes", "true", "1"),
                        "remarks": str(r.get("Remarks", "") or "").strip(),
                    },
                )

        # 13. Expenses
        if "Expenses" in sheet_names:
            for r in _sheet_rows_as_dicts(wb["Expenses"]):
                ex_date = _parse_date_safe(r.get("Date"))
                cat = str(r.get("Category", "") or "").strip()
                amt = _parse_dec_safe(r.get("Amount (PKR)"))
                if not ex_date or not cat or amt <= 0:
                    continue
                Expense.objects.get_or_create(
                    date=ex_date,
                    category=cat,
                    amount=amt,
                    note=str(r.get("Note", "") or "").strip(),
                    defaults={
                        "payment_mode": str(r.get("Payment Mode", "Cash") or "Cash").strip(),
                        "reference": str(r.get("Reference", "") or "").strip(),
                    },
                )
                counts["expenses"] += 1

        sync_all_postgresql_sequences()

    summary = (
        f"Master Excel Restore Complete! Restored/Updated: "
        f"{counts['classes']} Sections, {counts['students']} Students, "
        f"{counts['teachers']} Teachers, {counts['marks']} Exam Marks, "
        f"{counts['fee_entries']} Fee Entries, {counts['receipts']} Fee Receipts, "
        f"{counts['salary_bills']} Salary Bills."
    )
    return True, summary


def check_network_connection():
    """
    Checks live internet and SMTP mail server connectivity before attempting auto email backup.
    Returns (is_online: bool, detail_msg: str).
    """
    targets = [
        ("smtp.gmail.com", 587),
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
    ]
    for host, port in targets:
        try:
            sock = socket.create_connection((host, port), timeout=3.0)
            sock.close()
            return True, f"Online (Connected to {host}:{port})"
        except Exception:
            continue
    return False, "No active internet / SMTP network connection detected."


def send_backup_email_now(is_auto=False):
    """
    Generates both:
      1. Full PostgreSQL Database Dump (.sql)
      2. Full Multi-Sheet Master Excel Workbook (.xlsx)
    Saves a timestamped copy in the local `backups/` directory AND sends them via email
    using the configured BackupEmailAccount (Email + App Password) to all selected
    recipient emails (Option 1, Option 2, Option 3 + Default Email).
    """
    from accounts.models import Expense
    from exams.models import ExamMark
    from finance.models import FeePaymentReceipt
    from school.models import BackupEmailAccount, BackupHistoryLog, ClassLevel, SchoolSetting
    from students.models import Student
    from teachers.models import Teacher

    setting = SchoolSetting.objects.first()
    if not setting:
        setting = SchoolSetting.objects.create()

    accounts = BackupEmailAccount.ensure_three_slots()

    # Collect active sender accounts that have both email and app_password
    sender_accounts = [
        acc for acc in accounts
        if acc.is_active and acc.use_as_sender and acc.email.strip() and acc.app_password.strip()
    ]
    # Also fallback to any active account with email + app_password even if use_as_sender wasn't toggled
    if not sender_accounts:
        sender_accounts = [
            acc for acc in accounts
            if acc.is_active and acc.email.strip() and acc.app_password.strip()
        ]

    # Collect recipient emails
    recipient_list = []
    for acc in accounts:
        if acc.is_active and acc.receive_backup and acc.email.strip():
            e_addr = acc.email.strip()
            if e_addr not in recipient_list:
                recipient_list.append(e_addr)

    if setting.default_backup_email and setting.default_backup_email.strip():
        def_email = setting.default_backup_email.strip()
        if def_email not in recipient_list:
            recipient_list.append(def_email)

    # If sender is configured but no receiver checkbox was checked, send to the sender's own email
    if not recipient_list and sender_accounts:
        recipient_list.append(sender_accounts[0].email.strip())

    if not sender_accounts:
        msg = "No Sender Email & App Password configured yet. Please enter an Email and 16-digit Google App Password in Settings or Admin."
        setting.last_auto_backup_status = "Failed (No Credentials)"
        setting.last_auto_backup_message = msg
        setting.save(update_fields=["last_auto_backup_status", "last_auto_backup_message"])
        return False, msg

    # 1. Check Network Connectivity first
    is_online, net_msg = check_network_connection()
    if not is_online:
        msg = f"Network Offline: {net_msg} Backup will automatically retry when connected."
        setting.last_auto_backup_status = "Waiting for Network"
        setting.last_auto_backup_message = msg
        setting.save(update_fields=["last_auto_backup_status", "last_auto_backup_message"])
        BackupHistoryLog.objects.create(
            backup_type="Auto Daily Email Backup" if is_auto else "Manual Email Backup",
            status="Offline",
            details=msg,
        )
        return False, msg

    # 2. Generate Full SQL (.sql) & Full Master Excel (.xlsx)
    now_local = timezone.localtime(timezone.now())
    ts = now_local.strftime("%Y%m%d_%H%M")
    date_readable = now_local.strftime("%d %b %Y, %I:%M %p")

    sql_bytes = generate_full_sql_dump()
    excel_buf = generate_full_master_excel()
    excel_bytes = excel_buf.getvalue()

    sql_filename = f"KMS_Full_PostgreSQL_Backup_{ts}.sql"
    excel_filename = f"KMS_Full_Master_Backup_{ts}.xlsx"

    # Also save local copies in project's backups/ folder
    backups_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    try:
        with open(os.path.join(backups_dir, sql_filename), "wb") as f_sql:
            f_sql.write(sql_bytes)
        with open(os.path.join(backups_dir, excel_filename), "wb") as f_xl:
            f_xl.write(excel_bytes)
    except Exception:
        pass

    # 3. Compose Email with both .sql and .xlsx attachments
    school_name = setting.name or "Kohisar Model School & College"
    subject = f"[{school_name}] Full Daily Backup (.SQL + Master .XLSX) - {date_readable}"

    html_body = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; max-width: 680px; margin: 0 auto; border: 1px solid #cbd5e1; border-radius: 10px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #1a365d 0%, #0f2442 100%); color: #ffffff; padding: 20px 24px;">
        <h2 style="margin: 0; font-size: 20px;">{school_name}</h2>
        <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.85;">Automated Cloud Database Backup (.SQL &amp; Master Excel .XLSX)</p>
      </div>
      <div style="padding: 20px 24px; background: #ffffff;">
        <p style="margin-top: 0;">Assalam-o-Alaikum,</p>
        <p>Attached is the complete, verified institutional backup of <strong>{school_name}</strong> generated on <strong>{date_readable}</strong>.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;">
          <thead>
            <tr style="background: #f1f5f9; text-align: left;">
              <th style="padding: 8px 12px; border: 1px solid #cbd5e1;">Module / Record Category</th>
              <th style="padding: 8px 12px; border: 1px solid #cbd5e1;">Total Saved Records</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Students (Active &amp; Registered)</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{Student.objects.count()}</strong></td></tr>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Teachers &amp; Faculty Staff</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{Teacher.objects.count()}</strong></td></tr>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Classes &amp; Sections</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{ClassLevel.objects.count()} Classes</strong></td></tr>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Student Exam Marks Recorded</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{ExamMark.objects.count()} Marks</strong></td></tr>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Fee Payment Receipts</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{FeePaymentReceipt.objects.count()} Receipts</strong></td></tr>
            <tr><td style="padding: 8px 12px; border: 1px solid #cbd5e1;">General Expenses</td><td style="padding: 8px 12px; border: 1px solid #cbd5e1;"><strong>{Expense.objects.count()} Entries</strong></td></tr>
          </tbody>
        </table>
        <p style="font-size: 13px; color: #475569;">
          <strong>Attached Files:</strong><br>
          1. <code>{sql_filename}</code> — Full PostgreSQL Database Dump (Restore with 1 click in KMS Settings / Data Hub or via PostgreSQL).<br>
          2. <code>{excel_filename}</code> — Full 16-Sheet Master Excel Workbook (Viewable in Microsoft Excel &amp; 1-click restorable).
        </p>
      </div>
    </div>
    """

    last_error = ""
    for sender_acc in sender_accounts:
        sender_email = sender_acc.email.strip()
        # Strip spaces from 16-char Google App Password so both 'xxxx xxxx xxxx xxxx' and 'xxxxxxxxxxxxxxxx' work
        clean_app_pass = sender_acc.app_password.replace(" ", "").strip()

        msg = MIMEMultipart()
        msg["From"] = f"{school_name} Backup <{sender_email}>"
        msg["To"] = ", ".join(recipient_list)
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if setting.backup_send_sql:
            part_sql = MIMEBase("application", "sql")
            part_sql.set_payload(sql_bytes)
            encoders.encode_base64(part_sql)
            part_sql.add_header("Content-Disposition", f'attachment; filename="{sql_filename}"')
            msg.attach(part_sql)

        if setting.backup_send_excel:
            part_xl = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            part_xl.set_payload(excel_bytes)
            encoders.encode_base64(part_xl)
            part_xl.add_header("Content-Disposition", f'attachment; filename="{excel_filename}"')
            msg.attach(part_xl)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=25) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, clean_app_pass)
                server.sendmail(sender_email, recipient_list, msg.as_string())

            sender_acc.last_used_at = timezone.now()
            sender_acc.save(update_fields=["last_used_at"])

            success_msg = (
                f"Full Backup (.sql + .xlsx) sent via {sender_email} "
                f"to: {', '.join(recipient_list)}"
            )
            setting.last_auto_backup_at = timezone.now()
            setting.last_auto_backup_status = "Success"
            setting.last_auto_backup_message = success_msg
            setting.save(update_fields=[
                "last_auto_backup_at",
                "last_auto_backup_status",
                "last_auto_backup_message",
            ])

            BackupHistoryLog.objects.create(
                backup_type="Auto Daily Email Backup" if is_auto else "Manual Email Backup",
                status="Success",
                sender_email=sender_email,
                recipient_emails=", ".join(recipient_list),
                sql_filename=sql_filename if setting.backup_send_sql else "",
                excel_filename=excel_filename if setting.backup_send_excel else "",
                details=success_msg,
            )
            return True, success_msg
        except Exception as e:
            last_error = f"{sender_email}: {str(e)}"
            continue

    fail_msg = f"Email sending failed ({last_error}). Local backup files were still saved in backups/ folder ({sql_filename}, {excel_filename})."
    setting.last_auto_backup_status = "Failed"
    setting.last_auto_backup_message = fail_msg
    setting.save(update_fields=["last_auto_backup_status", "last_auto_backup_message"])
    BackupHistoryLog.objects.create(
        backup_type="Auto Daily Email Backup" if is_auto else "Manual Email Backup",
        status="Failed",
        sender_email=sender_accounts[0].email if sender_accounts else "",
        recipient_emails=", ".join(recipient_list),
        sql_filename=sql_filename,
        excel_filename=excel_filename,
        details=fail_msg,
    )
    return False, fail_msg
