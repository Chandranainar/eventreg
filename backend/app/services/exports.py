import csv
from io import BytesIO, StringIO

from app.models.registration import Registration

EXPORT_COLUMNS = [
    ("Timestamp", "created_at"),
    ("Registration ID", "registration_id"),
    ("Full name", "full_name"),
    ("Official Contact No", "normalised_phone"),
    ("Additional Contact No", "normalised_additional_phone"),
    ("Email Id", "email"),
    ("Qualification", "educational_qualification"),
    ("Age", "age"),
    ("Current City of Residence", "current_city"),
    ("Gender", "gender"),
    ("Profession", "profession"),
    ("Business / Company Name", "business_company_name"),
    ("Attendance", "attendance"),
    ("Food Preference", "food_preference"),
    ("Alpha School Alumni", "alpha_alumni"),
    ("Studied in Alpha School up to? (Standard)", "studied_standard"),
    ("Year of passing out from Alpha School", "year_of_passing"),
    ("Status", "registration_status"),
    ("Email status", "email_status"),
    ("Google Sheets sync status", "google_sheet_sync_status"),
    ("Source", "source"),
    ("Admin notes", "admin_notes"),
]


def safe_spreadsheet_value(value):
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def registrations_to_csv(registrations: list[Registration]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([heading for heading, _ in EXPORT_COLUMNS])
    for registration in registrations:
        writer.writerow([safe_spreadsheet_value(getattr(registration, attr)) for _, attr in EXPORT_COLUMNS])
    return output.getvalue()


def registrations_to_xlsx(registrations: list[Registration]) -> bytes:
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Registrations"
    sheet.append([heading for heading, _ in EXPORT_COLUMNS])
    for registration in registrations:
        sheet.append([safe_spreadsheet_value(getattr(registration, attr)) for _, attr in EXPORT_COLUMNS])
    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 40)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
