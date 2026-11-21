"""CSV and XLSX import/export helpers shared by the dashboard list views."""

import csv
import datetime as dt
import io
import re

from django.apps import apps
from django.db import transaction
from django.db.models import FileField
from django.forms import modelform_factory
from django.http import Http404, HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext as _


EXPORT_FORMATS = ("csv", "xlsx")
CSV_CONTENT_TYPE = "text/csv; charset=utf-8"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# Only these models are exposed through the dashboard import/export endpoints.
# The key is the lower-case Django app label + model name used in the URL.
DATASETS = {
    "core.booking": {
        "label": "Bookings",
        "list_url_name": "core:booking-list",
    },
    "core.servicerequest": {
        "label": "Service Requests",
        "list_url_name": "core:service-request-list",
    },
    "core.contactinquiry": {
        "label": "Contact Inquiries",
        "list_url_name": "core:contact-inquiry-list",
    },
    "core.vehiclerental": {
        "label": "Vehicle Rentals",
        "list_url_name": "core:vehicle-rental-list",
    },
    "core.paymentschedule": {
        "label": "Payment Schedules",
        "list_url_name": "core:payment-schedule-list",
    },
    "core.appointment": {
        "label": "Appointments",
        "list_url_name": "core:appointment-record-list",
    },
    "core.testimonial": {
        "label": "Testimonials",
        "list_url_name": "core:testimonial-list",
    },
    "core.weddingrecord": {
        "label": "Wedding Records",
        "list_url_name": "core:wedding-record-list",
    },
    "catalog.estate": {
        "label": "Estates",
        "list_url_name": "core:estate-list",
    },
    "catalog.vehicle": {
        "label": "Vehicles",
        "list_url_name": "core:vehicle-list",
    },
}


def normalize_format(value, default="csv"):
    """Return a supported format name, or ``None`` for an unknown value."""
    if not value:
        return default
    normalized = str(value).strip().lower().lstrip(".")
    return normalized if normalized in EXPORT_FORMATS else None


def format_from_filename(filename, default="csv"):
    """Infer the format from an uploaded file name."""
    name = (filename or "").lower()
    if name.endswith(".xlsx"):
        return "xlsx"
    if name.endswith(".csv"):
        return "csv"
    return default


def get_dataset(model_key):
    """Return ``(model, dataset_config)`` for a known dashboard list view."""
    try:
        dataset = DATASETS[model_key]
        model = apps.get_model(model_key)
    except (KeyError, LookupError, ValueError):
        raise Http404(_("Unknown dashboard dataset."))
    return model, dataset


def export_field_names(model):
    """Columns used for both export and import.

    ``id`` is included so an exported file can be imported again to update or
    recreate the same records. Auto-managed and file/image fields are left out: database
    timestamps must not be overwritten, and binary files are not portable in a
    CSV/XLSX round trip (the URL fields on Estate/Vehicle/Testimonial cover images).
    """
    names = ["id"]
    for field in model._meta.concrete_fields:
        if field.primary_key or not field.editable or isinstance(field, FileField):
            continue
        names.append(field.name)
    return names


def export_file(model, field_names, label, file_format="csv"):
    """Export records in the requested format."""
    if file_format == "xlsx":
        return export_xlsx(model, field_names, label)
    return export_csv(model, field_names, label)


def export_csv(model, field_names, label):
    response = HttpResponse(content_type=CSV_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="{slugify(label)}.csv"'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model.objects.all().order_by("pk").iterator():
        writer.writerow([_serialize(obj, name) for name in field_names])
    return response


def export_xlsx(model, field_names, label):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = _safe_sheet_title(label)
    sheet.append(field_names)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for obj in model.objects.all().order_by("pk").iterator():
        sheet.append([_serialize(obj, name) for name in field_names])

    for index in range(1, len(field_names) + 1):
        sheet.column_dimensions[get_column_letter(index)].width = 18

    stream = io.BytesIO()
    workbook.save(stream)
    response = HttpResponse(stream.getvalue(), content_type=XLSX_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="{slugify(label)}.xlsx"'
    return response


def _safe_sheet_title(label):
    cleaned = re.sub(r"[\\/*?:\[\]]", "", str(label or "Export")).strip()
    return cleaned[:31] or "Export"


def _serialize(obj, field_name):
    if field_name == "id":
        return obj.pk
    value = getattr(obj, obj._meta.get_field(field_name).attname)
    return "" if value is None else str(value)


def import_file(model, field_names, upload, file_format="csv"):
    """Import rows from an uploaded CSV or XLSX file.

    Returns ``(imported_count, errors)``. All rows are wrapped in one
    transaction, so a partially invalid file leaves the database untouched.
    """
    if file_format == "csv":
        fieldnames, rows, errors = _read_csv(upload)
    elif file_format == "xlsx":
        fieldnames, rows, errors = _read_xlsx(upload)
    else:
        return 0, [_("Unsupported file format.")]

    if errors:
        return 0, errors
    if not fieldnames:
        return 0, [_("The file is empty.")]

    form_class = modelform_factory(
        model, fields=[name for name in field_names if name != "id"]
    )
    form_field_names = list(form_class.base_fields)

    errors = []
    missing = [
        name for name, field in form_class.base_fields.items()
        if field.required and name not in fieldnames
    ]
    if missing:
        errors.append(
            _("Missing required column(s): %(fields)s")
            % {"fields": ", ".join(missing)}
        )
        return 0, errors

    imported = 0
    with transaction.atomic():
        for row_number, row in rows:
            row = {key: value for key, value in row.items() if key is not None}
            raw_id = str(row.get("id") or "").strip()
            instance = None

            if raw_id:
                try:
                    pk = int(raw_id)
                except (TypeError, ValueError):
                    pk = 0
                if pk < 1:
                    errors.append(
                        _("Row %(row)s: invalid id %(id)s.")
                        % {"row": row_number, "id": raw_id}
                    )
                    continue
                try:
                    instance = model.objects.get(pk=pk)
                except model.DoesNotExist:
                    # Keep the exported id so a backup can be restored into an
                    # empty table; Django will insert with that explicit pk.
                    instance = model(pk=pk)

            data = {
                name: "" if row.get(name) is None else row.get(name)
                for name in form_field_names
            }
            form = form_class(data=data, instance=instance)
            if form.is_valid():
                form.save()
                imported += 1
                continue

            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(
                        _("Row %(row)s: %(field)s %(error)s")
                        % {"row": row_number, "field": field, "error": error}
                    )

        if errors:
            transaction.set_rollback(True)

    return imported, errors


def import_csv(model, field_names, upload):
    """Backward-compatible wrapper for CSV imports."""
    return import_file(model, field_names, upload, "csv")


def _read_csv(upload):
    try:
        upload.seek(0)
        text = upload.read().decode("utf-8-sig")
    except (UnicodeDecodeError, AttributeError, ValueError):
        return [], [], [_("The CSV file must be UTF-8 encoded.")]

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return [], [], []

    fieldnames = [name.strip() if name else name for name in header]
    rows = []
    for row_number, values in enumerate(reader, start=2):
        if not any(value not in (None, "") for value in values):
            continue
        padded = list(values[:len(fieldnames)])
        padded.extend([""] * (len(fieldnames) - len(padded)))
        rows.append((row_number, dict(zip(fieldnames, padded))))
    return fieldnames, rows, []


def _read_xlsx(upload):
    try:
        from openpyxl import load_workbook
    except ImportError:
        return [], [], [_("XLSX support is not available.")]

    try:
        upload.seek(0)
        workbook = load_workbook(upload, read_only=True, data_only=True)
    except Exception:
        return [], [], [_("The XLSX file could not be read.")]

    try:
        sheet = workbook.active
        iterator = sheet.iter_rows(values_only=True)
        try:
            header = next(iterator)
        except StopIteration:
            return [], [], []

        fieldnames = [
            str(name).strip() if name is not None else ""
            for name in header
        ]
        rows = []
        for row_number, values in enumerate(iterator, start=2):
            if not any(value not in (None, "") for value in values):
                continue
            padded = list(values[:len(fieldnames)])
            padded.extend([""] * (len(fieldnames) - len(padded)))
            rows.append((
                row_number,
                {
                    name: _cell_text(value)
                    for name, value in zip(fieldnames, padded)
                },
            ))
        return fieldnames, rows, []
    finally:
        workbook.close()


def _cell_text(value):
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        value = value.date()
    if isinstance(value, (dt.date, dt.time)):
        return value.isoformat()
    return str(value)
