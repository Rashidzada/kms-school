from collections import defaultdict
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from school.excel_utils import create_styled_workbook, excel_download_response
from school.models import SchoolSetting
from finance.models import FeePaymentReceipt
from teachers.models import MonthlySalaryBill
from .forms import ExpenseForm
from .models import Expense


@login_required
def cashbook_summary(request):
    """
    Consolidated Cashbook view (FR-7.2):
    All fee receipts (income), all general expenses, and all paid salary bills (expense).
    Filterable by start_date and end_date.
    """
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    receipts = FeePaymentReceipt.objects.select_related("student").all()
    expenses = Expense.objects.all()
    salaries = MonthlySalaryBill.objects.filter(is_paid=True).select_related("teacher")

    if start_date:
        receipts = receipts.filter(payment_date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)
        salaries = salaries.filter(payment_date__gte=start_date)

    if end_date:
        receipts = receipts.filter(payment_date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)
        salaries = salaries.filter(payment_date__lte=end_date)

    # Combine into unified ledger items
    entries = []
    total_income = Decimal("0.00")
    total_expense = Decimal("0.00")

    for r in receipts:
        total_income += r.amount_paid
        entries.append({
            "date": r.payment_date,
            "type": "Income",
            "category": "Student Fee",
            "description": f"Receipt {r.receipt_no} - {r.student.full_name}",
            "reference": r.receipt_no,
            "income": r.amount_paid,
            "expense": Decimal("0.00"),
        })

    for e in expenses:
        total_expense += e.amount
        entries.append({
            "date": e.date,
            "type": "Expense",
            "category": e.category,
            "description": f"{e.category}: {e.note or 'Expense'}",
            "reference": e.reference or e.payment_mode,
            "income": Decimal("0.00"),
            "expense": e.amount,
        })

    for s in salaries:
        net = s.net_payable
        total_expense += net
        entries.append({
            "date": s.payment_date,
            "type": "Expense",
            "category": "Salary",
            "description": f"Salary: {s.teacher.full_name} ({s.month_name} {s.year})",
            "reference": s.voucher_no or f"VCH-{s.id}",
            "income": Decimal("0.00"),
            "expense": net,
        })

    # Sort most recent first
    entries.sort(key=lambda x: x["date"], reverse=True)
    net_balance = total_income - total_expense

    context = {
        "entries": entries,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "accounts/cashbook_summary.html", context)


@login_required
def add_expense(request):
    """
    Record an expense (FR-7.1).
    """
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save()
            messages.success(request, f"Expense of PKR {exp.amount} recorded under {exp.category}.")
            return redirect("cashbook_summary")
    else:
        form = ExpenseForm(initial={"date": timezone.now().date()})

    return render(request, "accounts/expense_form.html", {"form": form})


@login_required
def daily_summary(request):
    """
    Daily Summary report (FR-7.3):
    For every date with fee income, expense, or salary payment, show total income, total expenses, net.
    """
    daily_data = defaultdict(lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")})

    for r in FeePaymentReceipt.objects.all():
        daily_data[r.payment_date]["income"] += r.amount_paid

    for e in Expense.objects.all():
        daily_data[e.date]["expense"] += e.amount

    for s in MonthlySalaryBill.objects.filter(is_paid=True, payment_date__isnull=False):
        daily_data[s.payment_date]["expense"] += s.net_payable

    rows = []
    for d, val in sorted(daily_data.items(), key=lambda x: x[0], reverse=True):
        rows.append({
            "date": d,
            "income": val["income"],
            "expense": val["expense"],
            "net": val["income"] - val["expense"],
        })

    total_income = sum(r["income"] for r in rows)
    total_expense = sum(r["expense"] for r in rows)
    net_total = total_income - total_expense

    context = {
        "rows": rows,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_total": net_total,
    }
    return render(request, "accounts/daily_summary.html", context)


@login_required
def monthly_summary(request):
    """
    Monthly Summary report (FR-7.4):
    Income/expense/net rollup grouped by calendar month, most recent first.
    """
    monthly_data = defaultdict(lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")})

    for r in FeePaymentReceipt.objects.all():
        key = (r.payment_date.year, r.payment_date.month)
        monthly_data[key]["income"] += r.amount_paid

    for e in Expense.objects.all():
        key = (e.date.year, e.date.month)
        monthly_data[key]["expense"] += e.amount

    for s in MonthlySalaryBill.objects.filter(is_paid=True, payment_date__isnull=False):
        key = (s.payment_date.year, s.payment_date.month)
        monthly_data[key]["expense"] += s.net_payable

    import calendar
    rows = []
    for (year, month), val in sorted(monthly_data.items(), key=lambda x: (x[0][0], x[0][1]), reverse=True):
        rows.append({
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month] if 1 <= month <= 12 else f"Month {month}",
            "income": val["income"],
            "expense": val["expense"],
            "net": val["income"] - val["expense"],
        })

    total_income = sum(r["income"] for r in rows)
    total_expense = sum(r["expense"] for r in rows)
    net_total = total_income - total_expense

    context = {
        "rows": rows,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_total": net_total,
    }
    return render(request, "accounts/monthly_summary.html", context)


@login_required
def export_cashbook_excel(request):
    """
    Exports filtered or all cashbook records (Income & Expenses) to Excel.
    """
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    receipts = FeePaymentReceipt.objects.select_related("student").all()
    expenses = Expense.objects.all()
    salaries = MonthlySalaryBill.objects.filter(is_paid=True).select_related("teacher")

    if start_date:
        receipts = receipts.filter(payment_date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)
        salaries = salaries.filter(payment_date__gte=start_date)

    if end_date:
        receipts = receipts.filter(payment_date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)
        salaries = salaries.filter(payment_date__lte=end_date)

    entries = []
    for r in receipts:
        entries.append({
            "date": str(r.payment_date),
            "type": "Income",
            "category": "Student Fee",
            "description": f"Receipt #{r.receipt_no} - {r.student.full_name}",
            "reference": r.receipt_no,
            "income": float(r.amount_paid),
            "expense": 0.0,
        })

    for e in expenses:
        entries.append({
            "date": str(e.date),
            "type": "Expense",
            "category": e.category,
            "description": f"{e.category}: {e.note or 'Expense'}",
            "reference": e.reference or e.payment_mode or "-",
            "income": 0.0,
            "expense": float(e.amount),
        })

    for s in salaries:
        net = float(s.net_payable)
        entries.append({
            "date": str(s.payment_date),
            "type": "Expense",
            "category": "Staff Salary",
            "description": f"Salary: {s.teacher.full_name} ({s.month_name} {s.year})",
            "reference": s.voucher_no or f"VCH-{s.id}",
            "income": 0.0,
            "expense": net,
        })

    entries.sort(key=lambda x: x["date"], reverse=True)

    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Date",
        "Transaction Type",
        "Category",
        "Description",
        "Reference / Voucher",
        "Income (PKR)",
        "Expense (PKR)",
    ]

    rows = [
        [
            e["date"],
            e["type"],
            e["category"],
            e["description"],
            e["reference"],
            e["income"],
            e["expense"],
        ]
        for e in entries
    ]

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"Cashbook_{timestamp}.xlsx"
    buffer = create_styled_workbook("Cashbook Transactions Ledger", headers, rows, school_name=school_name)
    return excel_download_response(buffer, filename)


@login_required
def export_monthly_summary_excel(request):
    """
    Exports month-by-month financial statement rollup to Excel.
    """
    import calendar
    monthly_data = defaultdict(lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")})

    for r in FeePaymentReceipt.objects.all():
        key = (r.payment_date.year, r.payment_date.month)
        monthly_data[key]["income"] += r.amount_paid

    for e in Expense.objects.all():
        key = (e.date.year, e.date.month)
        monthly_data[key]["expense"] += e.amount

    for s in MonthlySalaryBill.objects.filter(is_paid=True, payment_date__isnull=False):
        key = (s.payment_date.year, s.payment_date.month)
        monthly_data[key]["expense"] += s.net_payable

    school = SchoolSetting.objects.first()
    school_name = school.name if school else "Kohisar Model School & College (KMS)"

    headers = [
        "Year",
        "Month",
        "Month Name",
        "Total Fee Collections (PKR)",
        "Total Expenses & Salaries (PKR)",
        "Net Operating Balance (PKR)",
        "Financial Status",
    ]

    rows = []
    for (year, month), val in sorted(monthly_data.items(), key=lambda x: (x[0][0], x[0][1]), reverse=True):
        income = float(val["income"])
        expense = float(val["expense"])
        net = income - expense
        status = "Surplus" if net > 0 else ("Deficit" if net < 0 else "Balanced")
        month_name = calendar.month_name[month] if 1 <= month <= 12 else f"Month {month}"
        rows.append([
            year,
            month,
            month_name,
            income,
            expense,
            net,
            status,
        ])

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"Monthly_Financial_Summary_{timestamp}.xlsx"
    buffer = create_styled_workbook("Monthly Financial Summary", headers, rows, school_name=school_name)
    return excel_download_response(buffer, filename)

