from django.urls import path
from . import views

urlpatterns = [
    path("", views.cashbook_summary, name="cashbook_summary"),
    path("add-expense/", views.add_expense, name="add_expense"),
    path("daily/", views.daily_summary, name="daily_summary"),
    path("monthly/", views.monthly_summary, name="monthly_summary"),
]
