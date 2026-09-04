from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.fee_register, name="fee_register"),
    path("collect/<int:student_id>/", views.collect_fee, name="collect_fee"),
    path("family-payment/<int:household_id>/", views.family_payment, name="family_payment"),
    path("adjust/<int:student_id>/", views.fee_adjust, name="fee_adjust"),
    path("receipt/<int:pk>/", views.fee_receipt, name="fee_receipt"),
    path("family-dues/", views.family_dues, name="family_dues"),
    path("class-summary/", views.class_fee_summary, name="class_fee_summary"),
    path("defaulters/", views.defaulters_list, name="defaulters_list"),
]
