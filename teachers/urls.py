from django.urls import path
from . import views

urlpatterns = [
    path("", views.teacher_list, name="teacher_list"),
    path("add/", views.teacher_create, name="teacher_create"),
    path("<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("<int:pk>/edit/", views.teacher_update, name="teacher_update"),
    path("<int:pk>/experience/", views.experience_certificate, name="experience_certificate"),
    path("<int:pk>/id-card/", views.staff_id_card, name="staff_id_card"),
    path("salary-scales/", views.salary_scale_list, name="salary_scale_list"),
    path("salary-bills/", views.salary_bill_list, name="salary_bill_list"),
    path("salary-bills/<int:pk>/", views.salary_bill_detail, name="salary_bill_detail"),
    path("salary-bills/<int:pk>/edit/", views.salary_bill_update, name="salary_bill_update"),
    path("salary-bills/generate/", views.generate_salary_bills, name="generate_salary_bills"),
]
