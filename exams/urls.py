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
]
