from django.urls import path
from . import views

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("export-excel/", views.export_students_excel, name="export_students_excel"),
    path("download-template/", views.download_student_template, name="download_student_template"),
    path("import-excel/", views.import_students_excel, name="import_students_excel"),
    path("add/", views.student_create, name="student_create"),
    path("blank-admission-form/", views.blank_admission_form, name="blank_admission_form"),
    path("admission-register/", views.admission_register, name="admission_register"),
    path("withdrawals/", views.withdrawal_register, name="withdrawal_register"),
    path("bulk-promote/", views.bulk_promote, name="bulk_promote"),
    path("families/", views.family_list, name="family_list"),
    path("families/add/", views.family_create, name="family_create"),
    path("families/<int:pk>/edit/", views.family_update, name="family_update"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/edit/", views.student_update, name="student_update"),
    path("<int:pk>/promote/", views.student_promote, name="student_promote"),
    path("<int:pk>/slc/", views.school_leaving_certificate, name="school_leaving_certificate"),
    path("<int:pk>/character/", views.character_certificate, name="character_certificate"),
    path("<int:pk>/dob-certificate/", views.dob_certificate, name="dob_certificate"),
    path("dob-certificate/", views.dob_certificate, name="dob_certificate_general"),
    path("<int:pk>/withdraw/", views.student_withdraw, name="student_withdraw"),
    path("<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("bulk-delete/", views.student_bulk_delete, name="student_bulk_delete"),
    path("class/<int:class_id>/delete/", views.class_students_delete, name="class_students_delete"),

    # Student QR Code, ID Cards & Attendance System (KMS V4)
    path("<int:pk>/qr-code/", views.student_qr_image, name="student_qr_image"),
    path("<int:pk>/id-card/", views.student_id_card, name="student_id_card"),
    path("id-cards/", views.all_student_id_cards, name="all_student_id_cards"),
    path("attendance/scan/", views.student_qr_attendance_scan, name="student_qr_attendance_scan"),
    path("attendance/api/scan/", views.api_process_student_qr_scan, name="api_process_student_qr_scan"),
    path("attendance/api/update/", views.api_update_student_attendance, name="api_update_student_attendance"),
    path("attendance/daily/", views.student_daily_attendance, name="student_daily_attendance"),
    path("attendance/daily/print/", views.student_daily_attendance_print, name="student_daily_attendance_print"),
    path("attendance/monthly-sheet/", views.student_monthly_attendance_sheet, name="student_monthly_attendance_sheet"),
    path("attendance/monthly-sheet/print/", views.student_monthly_attendance_print, name="student_monthly_attendance_print"),
    path("attendance/monthly-sheet/export-excel/", views.export_student_monthly_attendance_excel, name="export_student_monthly_attendance_excel"),
    path("attendance/yearly-sheet/", views.student_yearly_attendance_sheet, name="student_yearly_attendance_sheet"),
    path("attendance/yearly-sheet/export-excel/", views.export_student_yearly_attendance_excel, name="export_student_yearly_attendance_excel"),

    # Exam Fee & General Student Fee Collection Register
    path("fee-collection-list/", views.student_fee_collection_list, name="student_fee_collection_list"),
    path("fee-collection-list/export-excel/", views.export_student_fee_collection_excel, name="export_student_fee_collection_excel"),
]
