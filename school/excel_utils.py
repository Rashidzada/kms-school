"""
Excel Import / Export Utilities for Kohisar Model School & College (KMS)
Provides institutional styling, column auto-sizing, template generation,
and safe parsing of uploaded Excel spreadsheets.
"""
import io
import re
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from django.http import HttpResponse


# Institutional Palette
NAVY_HEADER = "1A365D"
GOLD_ACCENT = "D69E2E"
LIGHT_BG = "F7FAFC"
WHITE = "FFFFFF"
BORDER_COLOR = "CBD5E0"


def get_thin_border():
    thin = Side(border_style="thin", color=BORDER_COLOR)
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def create_styled_workbook(sheet_title, headers, rows, school_name="Kohisar Model School & College (KMS)"):
    """
    Creates a professionally formatted Excel spreadsheet with:
    - Institutional header banner
    - Deep navy column header row with bold white text
    - Formatted data cells with borders
    - Auto-adjusted column widths
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]  # Excel limits sheet names to 31 chars

    # 1. School Banner Row (Row 1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    banner_cell = ws.cell(row=1, column=1, value=f"{school_name} — {sheet_title}")
    banner_cell.font = Font(name="Calibri", size=14, bold=True, color=WHITE)
    banner_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    banner_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    # 2. Column Headers (Row 2)
    header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color=WHITE)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = get_thin_border()
    ws.row_dimensions[2].height = 26

    # 3. Data Rows (Row 3 onwards)
    border = get_thin_border()
    data_font = Font(name="Calibri", size=10)
    alt_fill = PatternFill(start_color="F0F4F8", end_color="F0F4F8", fill_type="solid")

    for row_idx, row_data in enumerate(rows, 3):
        is_alt = (row_idx % 2 == 0)
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = data_font
            cell.border = border
            if is_alt:
                cell.fill = alt_fill
            # Align numbers to right, text to left
            if isinstance(value, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[row_idx].height = 20

    # 4. Auto-fit column widths (with padding)
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        # Skip row 1 for length check because it's merged
        for cell in col[1:]:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Save to buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def excel_download_response(buffer, filename):
    """
    Wraps bytes buffer into standard Excel MIME download response.
    """
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def parse_excel_upload(uploaded_file, header_row=2):
    """
    Parses an uploaded Excel file.
    Expects header_row to define column keys.
    Returns: (list_of_dicts, list_of_errors)
    """
    try:
        wb = load_workbook(uploaded_file, data_only=True)
    except Exception as e:
        return None, [f"Invalid Excel file format: {str(e)}"]

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    if len(rows) < header_row:
        return None, ["Excel file does not contain enough rows (header missing)."]

    # Header is at header_row - 1 (0-indexed)
    raw_headers = rows[header_row - 1]
    # Clean headers: lowercase, alphanumeric and underscores only
    headers = []
    for h in raw_headers:
        if h is not None:
            clean_h = re.sub(r"[^a-z0-9]+", "_", str(h).lower()).strip("_")
            headers.append(clean_h)
        else:
            headers.append("")

    records = []
    for row_idx, row_values in enumerate(rows[header_row:], start=header_row + 1):
        # Skip empty rows
        if not any(row_values):
            continue
        row_dict = {}
        for col_idx, val in enumerate(row_values):
            if col_idx < len(headers) and headers[col_idx]:
                k = headers[col_idx]
                row_dict[k] = val

                # Auto-populate canonical key aliases for seamless lookups
                if "class_name" in k or k == "class":
                    row_dict["class_name"] = val
                elif "full_name" in k or k == "name":
                    row_dict["full_name"] = val
                elif "father" in k:
                    row_dict["father_name"] = val
                elif "monthly_fee" in k or "fee" in k:
                    row_dict["monthly_fee"] = val
                elif "level" in k:
                    row_dict["level"] = val
                elif "section" in k:
                    row_dict["sections"] = val
                    row_dict["section"] = val
                elif "staff_id" in k or "teacher_id" in k:
                    row_dict["staff_id"] = val
                    row_dict["teacher_id"] = val
                elif "designation" in k:
                    row_dict["designation"] = val
                elif "cnic" in k:
                    row_dict["cnic"] = val
                elif "birth" in k or "dob" in k:
                    row_dict["dob"] = val
                elif "joining" in k:
                    row_dict["joining_date"] = val
                elif "admission_date" in k:
                    row_dict["admission_date"] = val
                elif "admission_no" in k:
                    row_dict["admission_no"] = val
                elif "contact" in k or "phone" in k or "mobile" in k:
                    row_dict["contact_number"] = val
                elif "address" in k or "residence" in k:
                    row_dict["address"] = val
                    row_dict["residence"] = val
                elif "qualification" in k:
                    row_dict["qualification"] = val
                elif "experience" in k:
                    row_dict["experience"] = val
                elif "salary_scale" in k:
                    row_dict["salary_scale"] = val
                elif "status" in k:
                    row_dict["status"] = val

        row_dict["_row_number"] = row_idx
        records.append(row_dict)

    return records, []

