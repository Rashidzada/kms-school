from django.urls import path
from . import views

urlpatterns = [
    path("", views.cashbook_summary, name="cashbook_summary"),
    path("export-excel/", views.export_cashbook_excel, name="export_cashbook_excel"),
    path("add-expense/", views.add_expense, name="add_expense"),
    path("daily/", views.daily_summary, name="daily_summary"),
    path("monthly/", views.monthly_summary, name="monthly_summary"),
    path("monthly/export-excel/", views.export_monthly_summary_excel, name="export_monthly_summary_excel"),
]
