from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    GenerateSalaryBillsForm,
    MonthlySalaryBillForm,
    SalaryScaleForm,
    TeacherForm,
)
from .models import MonthlySalaryBill, SalaryScale, Teacher


@login_required
def teacher_list(request):
    """
    Teacher / Staff list (FR-6.3).
    """
    teachers = Teacher.objects.select_related("salary_scale").all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query)
            | Q(teacher_id__icontains=query)
            | Q(designation__icontains=query)
            | Q(contact_number__icontains=query)
        )
    if status:
        teachers = teachers.filter(status=status)

    return render(
        request,
        "teachers/teacher_list.html",
        {"teachers": teachers, "query": query, "selected_status": status},
    )


@login_required
def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher {teacher.full_name} added successfully.")
            return redirect("teacher_detail", pk=teacher.pk)
    else:
        form = TeacherForm()
    return render(request, "teachers/teacher_form.html", {"form": form, "title": "Add New Teacher / Staff"})


@login_required
def teacher_detail(request, pk):
    """
    Staff detail page showing profile plus full salary-bill history (most recent first) (FR-6.3).
    """
    teacher = get_object_or_404(
        Teacher.objects.select_related("salary_scale"), pk=pk
    )
    salary_bills = teacher.salary_bills.order_by("-year", "-month")
    return render(
        request,
        "teachers/teacher_detail.html",
        {"teacher": teacher, "salary_bills": salary_bills},
    )


@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Teacher {teacher.full_name} updated successfully.")
            return redirect("teacher_detail", pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(
        request,
        "teachers/teacher_form.html",
        {"form": form, "teacher": teacher, "title": f"Edit Teacher: {teacher.full_name}"},
    )


@login_required
def experience_certificate(request, pk):
    """
    Printable Staff Experience Certificate (FR-6.8, FR-8.3).
    """
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "teachers/experience_certificate.html", {"teacher": teacher})


@login_required
def staff_id_card(request, pk):
    """
    Printable Staff ID Card (FR-6.8, FR-8.3).
    """
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "teachers/staff_id_card.html", {"teacher": teacher})


@login_required
def salary_bill_list(request):
    """
    Salary bill list filterable by month and year (FR-6.7).
    """
    today = timezone.now().date()
    month = request.GET.get("month", str(today.month))
    year = request.GET.get("year", str(today.year))

    bills = MonthlySalaryBill.objects.select_related("teacher").all()
    if month:
        bills = bills.filter(month=int(month))
    if year:
        bills = bills.filter(year=int(year))

    total_net = sum(b.net_payable for b in bills)
    total_paid = sum(b.net_payable for b in bills if b.is_paid)

    import calendar
    context = {
        "bills": bills,
        "selected_month": int(month) if month else "",
        "selected_year": int(year) if year else "",
        "selected_month_name": calendar.month_name[int(month)] if month else "All Months",
        "total_net": total_net,
        "total_paid": total_paid,
        "months": [(i, calendar.month_name[i]) for i in range(1, 13)],
    }
    return render(request, "teachers/salary_bill_list.html", context)


@login_required
def salary_bill_detail(request, pk):
    """
    Printable Salary Bill / Slip detail view (FR-6.7, FR-8.4).
    """
    bill = get_object_or_404(
        MonthlySalaryBill.objects.select_related("teacher", "teacher__salary_scale"),
        pk=pk,
    )
    return render(request, "teachers/salary_bill_detail.html", {"bill": bill})


@login_required
def salary_bill_update(request, pk):
    """
    Edit individual salary bill (FR-6.6).
    """
    bill = get_object_or_404(MonthlySalaryBill, pk=pk)
    if request.method == "POST":
        form = MonthlySalaryBillForm(request.POST, instance=bill)
        if form.is_valid():
            updated_bill = form.save(commit=False)
            if updated_bill.is_paid and not updated_bill.payment_date:
                updated_bill.payment_date = timezone.now().date()
            updated_bill.save()
            messages.success(request, f"Salary bill for {bill.teacher.full_name} updated.")
            return redirect("salary_bill_list")
    else:
        form = MonthlySalaryBillForm(instance=bill)

    return render(
        request,
        "teachers/salary_bill_form.html",
        {"form": form, "bill": bill},
    )


@login_required
def generate_salary_bills(request):
    """
    Batch generate salary bills for active teachers with assigned salary scales (FR-6.4, Rule 9).
    """
    today = timezone.now().date()
    if request.method == "POST":
        form = GenerateSalaryBillsForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])

            active_teachers = Teacher.objects.filter(
                status="Active", salary_scale__isnull=False
            ).select_related("salary_scale")

            created_count = 0
            with transaction.atomic():
                for teacher in active_teachers:
                    if not MonthlySalaryBill.objects.filter(
                        teacher=teacher, month=month, year=year
                    ).exists():
                        scale = teacher.salary_scale
                        MonthlySalaryBill.objects.create(
                            teacher=teacher,
                            month=month,
                            year=year,
                            base_pay=scale.basic_pay,
                            days_present=30,
                            allowances=scale.total_allowances,
                            deductions=Decimal("0.00"),
                            is_paid=False,
                        )
                        created_count += 1

            messages.success(
                request,
                f"Generated {created_count} salary bills for {month}/{year}.",
            )
            return redirect(f"/teachers/salary-bills/?month={month}&year={year}")
    else:
        form = GenerateSalaryBillsForm(initial={"month": today.month, "year": today.year})

    return render(
        request, "teachers/generate_salary_bills.html", {"form": form}
    )


@login_required
def salary_scale_list(request):
    scales = SalaryScale.objects.all()
    if request.method == "POST":
        form = SalaryScaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salary scale added successfully.")
            return redirect("salary_scale_list")
    else:
        form = SalaryScaleForm()
    return render(
        request, "teachers/salary_scale_list.html", {"scales": scales, "form": form}
    )
