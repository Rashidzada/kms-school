from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("excel-hub/", views.excel_data_hub, name="excel_data_hub"),
    path("backup/", views.download_db_backup, name="download_db_backup"),
    path("settings/", views.school_settings, name="school_settings"),
    path("sessions/", views.session_list, name="session_list"),
    path("classes/", views.class_list, name="class_list"),
    path("classes/export-excel/", views.export_classes_excel, name="export_classes_excel"),
    path("classes/download-template/", views.download_class_template, name="download_class_template"),
    path("classes/import-excel/", views.import_classes_excel, name="import_classes_excel"),
    path("sections/add/", views.section_create, name="section_create"),
]
