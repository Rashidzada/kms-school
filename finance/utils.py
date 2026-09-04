from decimal import Decimal
from django.db import transaction
from .models import StudentFeeMonthEntry


def initialize_ledger_months(
    ledger, student, class_monthly_fee=None, admission_date=None, withdrawal_date=None
):
    """
    Initializes 12 monthly fee entries (Jan-Dec) for a StudentFeeLedger.
    Zeroes months strictly before admission and strictly after withdrawal.
    """
    if class_monthly_fee is None:
        class_monthly_fee = (
            student.current_class.monthly_fee
            if student.current_class
            else Decimal("0.00")
        )

    admission_month = admission_date.month if admission_date else None
    withdrawal_month = withdrawal_date.month if withdrawal_date else None

    # Check session date range for admission
    session = ledger.academic_session
    adm_date = student.admission_date
    if adm_date and session.start_date <= adm_date <= session.end_date:
        admission_month = adm_date.month

    entries = []
    for m in range(1, 13):
        fee = class_monthly_fee
        if admission_month and m < admission_month:
            fee = Decimal("0.00")
        if withdrawal_month and m > withdrawal_month:
            fee = Decimal("0.00")

        entry = StudentFeeMonthEntry(
            ledger=ledger,
            month=m,
            arrears=Decimal("0.00"),
            monthly_fee=fee,
            exam_fee=Decimal("0.00"),
            other_charges=Decimal("0.00"),
            paid_amount=Decimal("0.00"),
            is_paid=False,
        )
        entries.append(entry)

    StudentFeeMonthEntry.objects.bulk_create(entries)
    recalculate_ledger_arrears(ledger)


def recalculate_ledger_arrears(ledger):
    """
    Recalculates month-by-month arrears roll-forward:
    For month 2..12, arrears = previous month's balance (total_amount - paid_amount).
    Refreshes is_paid flag on each entry.
    """
    entries = list(ledger.monthly_entries.order_by("month"))
    if not entries:
        return

    prev_balance = Decimal("0.00")
    for idx, entry in enumerate(entries):
        if idx > 0:
            entry.arrears = max(Decimal("0.00"), prev_balance)

        # Refresh is_paid flag
        entry.is_paid = (entry.paid_amount or Decimal("0.00")) >= entry.total_amount
        entry.save(
            update_fields=["arrears", "is_paid", "last_payment_date", "last_receipt_no"]
        )

        prev_balance = entry.balance


def apply_withdrawal_stop(student, withdrawal_date):
    """
    When a student is withdrawn, zeroes monthly_fee, exam_fee, and other_charges
    for all months strictly after the withdrawal month, then recalculates arrears.
    """
    from .models import StudentFeeLedger

    # Find the ledger for session containing withdrawal_date or most recent
    ledger = StudentFeeLedger.objects.filter(
        student=student,
        academic_session__start_date__lte=withdrawal_date,
        academic_session__end_date__gte=withdrawal_date,
    ).first()

    if not ledger:
        ledger = StudentFeeLedger.objects.filter(student=student).first()

    if ledger:
        w_month = withdrawal_date.month
        ledger.monthly_entries.filter(month__gt=w_month).update(
            monthly_fee=Decimal("0.00"),
            exam_fee=Decimal("0.00"),
            other_charges=Decimal("0.00"),
        )
        recalculate_ledger_arrears(ledger)


def roll_over_arrears(student, from_session, to_session):
    """
    Rolls over outstanding balance from the end of from_session into
    Month 1 of to_session.
    """
    from .models import StudentFeeLedger

    old_ledger = StudentFeeLedger.objects.filter(
        student=student, academic_session=from_session
    ).first()
    new_ledger = StudentFeeLedger.objects.filter(
        student=student, academic_session=to_session
    ).first()

    if old_ledger and new_ledger:
        last_entry = old_ledger.monthly_entries.filter(month=12).first()
        outstanding = last_entry.balance if last_entry else Decimal("0.00")
        first_entry = new_ledger.monthly_entries.filter(month=1).first()
        if first_entry:
            first_entry.arrears = max(Decimal("0.00"), outstanding)
            first_entry.save(update_fields=["arrears"])
            recalculate_ledger_arrears(new_ledger)
