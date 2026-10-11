from django.urls import path
from . import views

urlpatterns = [
    path("", views.teacher_list, name="teacher_list"),
    path("export-excel/", views.export_teachers_excel, name="export_teachers_excel"),
    path("download-template/", views.download_teacher_template, name="download_teacher_template"),
    path("import-excel/", views.import_teachers_excel, name="import_teachers_excel"),
    path("add/", views.teacher_create, name="teacher_create"),
    path("<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("<int:pk>/edit/", views.teacher_update, name="teacher_update"),
    path("<int:pk>/experience/", views.experience_certificate, name="experience_certificate"),
    path("<int:pk>/id-card/", views.staff_id_card, name="staff_id_card"),
    path("id-cards/bulk/", views.all_staff_id_cards, name="all_staff_id_cards"),
    path("<int:pk>/qr-code/", views.teacher_qr_image, name="teacher_qr_image"),
    
    # KMS V4 Teacher Attendance & QR Code System Routes
    path("attendance/scan/", views.qr_attendance_scan, name="qr_attendance_scan"),
    path("attendance/api/scan/", views.api_process_qr_scan, name="api_process_qr_scan"),
    path("attendance/api/update/", views.api_update_teacher_attendance, name="api_update_teacher_attendance"),
    path("attendance/daily/", views.daily_attendance_register, name="daily_attendance_register"),
    path("attendance/daily/print/", views.daily_attendance_print, name="daily_attendance_print"),
    path("attendance/biometric-import/", views.biometric_fingerprint_import, name="biometric_fingerprint_import"),
    path("attendance/monthly-sheet/", views.monthly_attendance_sheet, name="monthly_attendance_sheet"),
    path("attendance/monthly-sheet/print/", views.monthly_attendance_print, name="monthly_attendance_print"),
    path("attendance/monthly-sheet/export-excel/", views.export_monthly_attendance_excel, name="export_monthly_attendance_excel"),
    path("attendance/yearly-sheet/", views.yearly_attendance_sheet, name="yearly_attendance_sheet"),
    path("attendance/yearly-sheet/export-excel/", views.export_yearly_attendance_excel, name="export_yearly_attendance_excel"),
    path("attendance/settings/", views.attendance_settings_view, name="attendance_settings"),
    path("attendance/qr-cards/", views.all_staff_qr_cards, name="all_staff_qr_cards"),

    # Salary Scales & Bills
    path("salary-scales/", views.salary_scale_list, name="salary_scale_list"),
    path("salary-bills/", views.salary_bill_list, name="salary_bill_list"),
    path("salary-bills/export-excel/", views.export_salary_bills_excel, name="export_salary_bills_excel"),
    path("salary-bills/<int:pk>/", views.salary_bill_detail, name="salary_bill_detail"),
    path("salary-bills/<int:pk>/edit/", views.salary_bill_update, name="salary_bill_update"),
    path("salary-bills/<int:pk>/sync-attendance/", views.sync_salary_bill_attendance_view, name="sync_salary_bill_attendance"),
    path("salary-bills/generate/", views.generate_salary_bills, name="generate_salary_bills"),

    # Teacher Loans & Advances
    path("loans/", views.teacher_loan_list, name="teacher_loan_list"),
    path("loans/add/", views.teacher_loan_create, name="teacher_loan_create"),
    path("loans/<int:pk>/", views.teacher_loan_detail, name="teacher_loan_detail"),
    path("loans/<int:pk>/delete/", views.teacher_loan_delete, name="teacher_loan_delete"),
]

