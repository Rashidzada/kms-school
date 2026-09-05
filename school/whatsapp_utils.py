"""
WhatsApp Messaging Utilities for Kohisar Model School & College (KMS)
Provides one-click WhatsApp message generation with Islamic greetings (Salam),
financial dues breakdowns, family linkages, and direct https://wa.me/ links.
"""

import re
import urllib.parse
from decimal import Decimal


def clean_whatsapp_number(phone):
    """
    Normalizes local Pakistani phone numbers (e.g., 0347-0983567, 03001234567, +92347...)
    to the international format required by WhatsApp (923470983567).
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("0092"):
        digits = digits[2:]
    elif digits.startswith("03") and len(digits) == 11:
        digits = "92" + digits[1:]
    elif digits.startswith("3") and len(digits) == 10:
        digits = "92" + digits
    elif digits.startswith("92") and len(digits) == 12:
        pass  # already standard international
    return digits


def build_wa_link(phone, text):
    """
    Constructs a direct WhatsApp web/mobile URL.
    If phone is present, directs to that chat. If empty, opens WhatsApp to pick contact.
    """
    clean_phone = clean_whatsapp_number(phone)
    encoded_text = urllib.parse.quote(text)
    if clean_phone:
        return f"https://wa.me/{clean_phone}?text={encoded_text}"
    return f"https://wa.me/?text={encoded_text}"


# Default school leadership contacts
PRINCIPAL_NAME = "Farman Ali"
PRINCIPAL_CONTACT = "0344-9631323"
VP_NAME = "Umar Saeed"
VP_CONTACT = "0345-3407095"


def build_student_fee_receipt_msg(
    receipt,
    student,
    months_covered_names,
    total_billed_sum,
    this_receipt_months_dues_left,
    student_total_dues_left,
    family_total_dues_left=Decimal("0.00"),
    family_count=0,
    principal_name=PRINCIPAL_NAME,
    principal_contact=PRINCIPAL_CONTACT,
    vp_name=VP_NAME,
    vp_contact=VP_CONTACT,
):
    """
    Generates a polite Islamic WhatsApp confirmation message for a student fee receipt.
    """
    raw_phone = student.contact_number or (student.family.contact_number if student.family else "")
    clean_phone = clean_whatsapp_number(raw_phone)

    family_line = ""
    if family_total_dues_left and family_total_dues_left > 0:
        family_line = f"• *Family Total Dues ({family_count} siblings):* Rs. {family_total_dues_left:,.0f}\n"

    date_str = receipt.payment_date.strftime("%d-%b-%Y") if receipt.payment_date else ""

    text = (
        "السلام علیکم ورحمۃ اللہ وبرکاتہ\n"
        "Assalam-o-Alaikum Dear Parent / Guardian,\n\n"
        "Official fee receipt confirmation from *Kohisar Model School & College (KMS), Qalagay Swat*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *STUDENT & RECEIPT DETAILS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Student Name:* {student.full_name}\n"
        f"• *Father's Name:* {student.father_name}\n"
        f"• *Admission No:* {student.admission_no}\n"
        f"• *Class & Section:* {student.current_class.name} - {student.current_section.name}\n"
        f"• *Receipt No:* {receipt.receipt_no}\n"
        f"• *Payment Date:* {date_str}\n"
        f"• *Months Covered:* {months_covered_names}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💳 *PAYMENT & DUES SUMMARY*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Total Billed:* Rs. {total_billed_sum:,.0f}\n"
        f"• *Amount Paid:* Rs. {receipt.amount_paid:,.0f} ✅\n"
        f"• *This Month Remaining Dues:* Rs. {this_receipt_months_dues_left:,.0f}\n"
        f"• *Student Total Outstanding Dues:* Rs. {student_total_dues_left:,.0f}\n"
        f"{family_line}"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Notice:* Fee once paid will not be returned in any case.\n\n"
        f"📞 Principal: {principal_name} ({principal_contact})\n"
        f"📞 Vice Principal: {vp_name} ({vp_contact})\n\n"
        "JazakAllah Khair!\n"
        "*Kohisar Model School & College, Qalagay Swat*"
    )

    return {
        "text": text,
        "url": build_wa_link(clean_phone, text),
        "raw_phone": raw_phone,
        "clean_phone": clean_phone,
    }


def build_student_dues_reminder_msg(
    student,
    student_total_dues,
    pending_months_summary="",
    family_total_dues=Decimal("0.00"),
    family_count=0,
    principal_name=PRINCIPAL_NAME,
    principal_contact=PRINCIPAL_CONTACT,
    vp_name=VP_NAME,
    vp_contact=VP_CONTACT,
):
    """
    Generates a respectful Islamic WhatsApp fee reminder for a student/parent.
    """
    raw_phone = student.contact_number or (student.family.contact_number if student.family else "")
    clean_phone = clean_whatsapp_number(raw_phone)

    months_line = ""
    if pending_months_summary:
        months_line = f"• *Pending Months:* {pending_months_summary}\n"

    family_line = ""
    if family_total_dues and family_total_dues > 0:
        family_line = f"• *Family Total Dues ({family_count} siblings):* Rs. {family_total_dues:,.0f}\n"

    text = (
        "السلام علیکم ورحمۃ اللہ وبرکاتہ\n"
        "Assalam-o-Alaikum Dear Parent / Guardian,\n\n"
        "Respectful fee reminder from *Kohisar Model School & College (KMS), Qalagay Swat*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *STUDENT DUES DETAILS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Student Name:* {student.full_name}\n"
        f"• *Father's Name:* {student.father_name}\n"
        f"• *Admission No:* {student.admission_no}\n"
        f"• *Class & Section:* {student.current_class.name} - {student.current_section.name}\n"
        f"{months_line}"
        f"• *Total Outstanding Dues:* Rs. {student_total_dues:,.0f}\n"
        f"{family_line}"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Kindly clear the pending fee at your earliest convenience to keep records updated.\n\n"
        f"📞 Principal: {principal_name} ({principal_contact})\n"
        f"📞 Vice Principal: {vp_name} ({vp_contact})\n\n"
        "JazakAllah Khair!\n"
        "*Kohisar Model School & College, Qalagay Swat*"
    )

    return {
        "text": text,
        "url": build_wa_link(clean_phone, text),
        "raw_phone": raw_phone,
        "clean_phone": clean_phone,
    }


def build_family_dues_reminder_msg(
    family,
    fam_students,
    total_dues,
    unpaid_months_count=0,
    principal_name=PRINCIPAL_NAME,
    principal_contact=PRINCIPAL_CONTACT,
    vp_name=VP_NAME,
    vp_contact=VP_CONTACT,
):
    """
    Generates a respectful Islamic WhatsApp dues reminder for a whole family household.
    """
    raw_phone = family.contact_number
    clean_phone = clean_whatsapp_number(raw_phone)

    student_names = ", ".join([f"{s.full_name} ({s.current_class.name})" for s in fam_students])

    text = (
        "السلام علیکم ورحمۃ اللہ وبرکاتہ\n"
        f"Assalam-o-Alaikum Respected {family.father_guardian_name},\n\n"
        "Family fee summary reminder from *Kohisar Model School & College (KMS), Qalagay Swat*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👨‍👩‍👧‍👦 *FAMILY ACCOUNT SUMMARY*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Family ID:* {family.family_id}\n"
        f"• *Father / Guardian:* {family.father_guardian_name}\n"
        f"• *Enrolled Children ({len(fam_students)}):* {student_names}\n"
        f"• *Unpaid Months Count:* {unpaid_months_count}\n"
        f"• *Total Family Outstanding Dues:* Rs. {total_dues:,.0f}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Kindly clear the pending family fee at your earliest convenience.\n\n"
        f"📞 Principal: {principal_name} ({principal_contact})\n"
        f"📞 Vice Principal: {vp_name} ({vp_contact})\n\n"
        "JazakAllah Khair!\n"
        "*Kohisar Model School & College, Qalagay Swat*"
    )

    return {
        "text": text,
        "url": build_wa_link(clean_phone, text),
        "raw_phone": raw_phone,
        "clean_phone": clean_phone,
    }


def build_teacher_salary_slip_msg(
    bill,
    principal_name=PRINCIPAL_NAME,
    principal_contact=PRINCIPAL_CONTACT,
    vp_name=VP_NAME,
    vp_contact=VP_CONTACT,
):
    """
    Generates a respectful Islamic WhatsApp salary statement message for a faculty/staff member.
    """
    teacher = bill.teacher
    raw_phone = teacher.contact_number
    clean_phone = clean_whatsapp_number(raw_phone)

    date_str = bill.payment_date.strftime("%d-%b-%Y") if bill.payment_date else "Pending Disbursement"
    daily_rate = getattr(bill, "daily_rate", (bill.base_pay / Decimal("30.0")) if bill.base_pay else Decimal("0.00"))
    if bill.absent_days > 0:
        absent_line = f"• *Absence Deduction ({bill.absent_days} days @ Rs. {daily_rate:,.0f}/day):* Rs. {bill.auto_absent_deduction:,.0f}\n"
    else:
        absent_line = "• *Absence Deduction:* Nil (Full Attendance - 30/30 days) ✅\n"

    other_line = ""
    if bill.other_deductions > 0:
        other_line = f"• *Other Deductions:* Rs. {bill.other_deductions:,.0f}\n"

    text = (
        "السلام علیکم ورحمۃ اللہ وبرکاتہ\n"
        f"Assalam-o-Alaikum Respected {teacher.full_name},\n\n"
        "Monthly salary slip statement from *Kohisar Model School & College (KMS), Qalagay Swat*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👨‍🏫 *FACULTY / SALARY BILL DETAILS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Staff ID:* {teacher.teacher_id}\n"
        f"• *Faculty Member:* {teacher.full_name}\n"
        f"• *Designation:* {teacher.designation}\n"
        f"• *Salary Month:* {bill.month_name} {bill.year}\n"
        f"• *Voucher No:* SAL-{bill.id}\n"
        f"• *Payment Date:* {date_str}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💵 *SALARY & DEDUCTIONS BREAKDOWN*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Basic Pay:* Rs. {bill.base_pay:,.0f}\n"
        f"• *Allowances:* Rs. {bill.allowances:,.0f}\n"
        f"• *Gross Monthly Earnings:* Rs. {bill.gross_pay:,.0f}\n"
        f"{absent_line}"
        f"{other_line}"
        f"• *Total Deductions:* Rs. {bill.deductions:,.0f}\n"
        f"• *Net Payable Monthly Salary:* Rs. {bill.net_payable:,.0f}\n"
        f"• *Amount Disbursed / Paid:* Rs. {bill.actual_paid:,.0f} ✅\n"
        f"• *Remaining Balance Left:* Rs. {bill.balance_left:,.0f}\n"
        f"• *Status:* {bill.payment_status.upper()}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Thank you for your dedicated service and commitment to our students.\n\n"
        f"📞 Principal: {principal_name} ({principal_contact})\n"
        f"📞 Vice Principal: {vp_name} ({vp_contact})\n\n"
        "JazakAllah Khair!\n"
        "*Kohisar Model School & College, Qalagay Swat*"
    )

    return {
        "text": text,
        "url": build_wa_link(clean_phone, text),
        "raw_phone": raw_phone,
        "clean_phone": clean_phone,
    }