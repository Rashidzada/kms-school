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
]
