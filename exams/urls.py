from django.urls import path
from . import views

urlpatterns = [
    path("", views.exam_dashboard, name="exam_dashboard"),
    path("list/", views.exam_list, name="exam_list"),
    path("create/", views.exam_create, name="exam_create"),
    path("<int:pk>/edit/", views.exam_edit, name="exam_edit"),
    path("subjects/", views.subject_manage, name="subject_manage"),
    path("award-sheet/", views.subject_award_sheet, name="subject_award_sheet"),
    path("award-sheet/export/", views.export_subject_award_excel, name="export_subject_award_excel"),
    path("award-sheet/import/", views.import_subject_award_excel, name="import_subject_award_excel"),
    path("award-sheet/print/", views.print_subject_award_sheet, name="print_subject_award_sheet"),
    path("enter-marks/", views.class_marks_entry_grid, name="class_marks_entry_grid"),
    path("class-marks/reset/", views.class_marks_reset, name="class_marks_reset"),
    path("bulk-dmc/", views.bulk_dmc_print, name="bulk_dmc_print"),
    path("class-template/export/", views.export_class_template_excel, name="export_class_template_excel"),
    path("class-result/import/", views.import_class_result_excel, name="import_class_result_excel"),
    path("class-result/", views.class_result_sheet, name="class_result_sheet"),
    path("class-result/export/", views.export_class_result_excel, name="export_class_result_excel"),
    path("class-result/print/", views.print_class_result_sheet, name="print_class_result_sheet"),
    path("dmc/<int:student_id>/<int:exam_id>/", views.student_dmc, name="student_dmc"),
    path("roll-numbers/", views.roll_number_slips, name="roll_number_slips"),
    path("roll-number/<int:student_id>/", views.single_student_roll_number_slip, name="student_roll_number_slip"),
    path("roll-number/<int:student_id>/<int:exam_id>/", views.single_student_roll_number_slip, name="student_roll_number_slip_exam"),
    path("blank-sheet/", views.blank_marks_sheet, name="blank_marks_sheet"),
    path("blank-sheet/export/", views.export_blank_marks_excel, name="export_blank_marks_excel"),

    # Wing & Whole-School Master Result Books
    path("wing-result/", views.wing_result_book, name="wing_result_book"),
    path("wing-result/print/", views.print_wing_result_book, name="print_wing_result_book"),
    path("wing-result/export/", views.export_wing_result_book_excel, name="export_wing_result_book_excel"),

    # Consolidated Annual Results (All Terms Cumulative & Top Position Holders)
    path("consolidated-annual/", views.consolidated_annual_result, name="consolidated_annual_result"),
    path("consolidated-annual/print/", views.print_consolidated_annual_result, name="print_consolidated_annual_result"),
    path("consolidated-annual/export/", views.export_consolidated_annual_excel, name="export_consolidated_annual_excel"),

    # Student Multi-Term Academic History & Transcripts
    path("student-history/", views.student_exam_history, name="student_exam_history"),
    path("student-history/<int:student_id>/", views.student_exam_history, name="student_exam_history_detail"),
    path("student-history/<int:student_id>/print/", views.print_student_exam_history, name="print_student_exam_history"),

    # Full Exam Marks & Curriculum Real Backup & Restore (.xlsx)
    path("backup/export-excel/", views.export_all_exams_backup_excel, name="export_all_exams_backup_excel"),
    path("backup/import-excel/", views.import_all_exams_backup_excel, name="import_all_exams_backup_excel"),
]

