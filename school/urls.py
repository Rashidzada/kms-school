from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("excel-hub/", views.excel_data_hub, name="excel_data_hub"),
    path("backup/", views.download_db_backup, name="download_db_backup"),
    path("backup/master-excel/", views.download_master_excel_backup, name="download_master_excel_backup"),
    path("backup/restore/", views.restore_full_database, name="restore_full_database"),
    path("backup/api/check-network/", views.api_check_backup_network, name="api_check_backup_network"),
    path("backup/api/run-email-backup/", views.api_run_email_backup, name="api_run_email_backup"),
    path("settings/", views.school_settings, name="school_settings"),
    path("sessions/", views.session_list, name="session_list"),
    path("classes/", views.class_list, name="class_list"),
    path("classes/export-excel/", views.export_classes_excel, name="export_classes_excel"),
    path("classes/download-template/", views.download_class_template, name="download_class_template"),
    path("classes/import-excel/", views.import_classes_excel, name="import_classes_excel"),
    path("sections/add/", views.section_create, name="section_create"),
    path("sections/<int:pk>/update-teacher/", views.section_update_teacher, name="section_update_teacher"),

    # Software License & Subscription Management (Vendor / Developer Portal)
    path("license/expired/", views.license_expired, name="license_expired"),
    path("license/portal/", views.license_developer_portal, name="license_developer_portal"),
]

