from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("backup/", views.download_db_backup, name="download_db_backup"),
    path("settings/", views.school_settings, name="school_settings"),
    path("sessions/", views.session_list, name="session_list"),
    path("classes/", views.class_list, name="class_list"),
    path("sections/add/", views.section_create, name="section_create"),
]
