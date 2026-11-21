from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from catalog.models import Estate
from .forms import AppointmentForm, BookingEnquiryForm, ContactInquiryForm, ServiceRequestForm
from .marketing import RESULTS_YEAR, results_snapshot, testimonial_rating
from .models import Appointment, ContactInquiry, ServiceRequest, Testimonial


@require_http_methods(["GET", "POST"])
def booking_enquiry(request, slug):
    estate = get_object_or_404(Estate, slug=slug, is_published=True)
    form = BookingEnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.estate = estate
        booking.quoted_estate_total = estate.price_from
        if request.user.is_authenticated:
            booking.user = request.user
        booking.save()
        messages.success(request, "Your enquiry has been received. We will contact you about availability.")
        return redirect(estate.get_absolute_url())
    return render(request, "core/enquiry.html", {"form": form, "estate": estate})


@require_http_methods(["GET", "POST"])
def needs(request):
    return redirect("/contact/?tab=request")


@require_http_methods(["GET", "POST"])
def contact(request):
    enquiry_form = ContactInquiryForm(request.POST or None, prefix="enquiry") if (request.method == "POST" and request.POST.get("form_type") == "enquiry") else ContactInquiryForm(prefix="enquiry")
    request_form = ServiceRequestForm(request.POST or None, prefix="request") if (request.method == "POST" and request.POST.get("form_type") == "request") else ServiceRequestForm(prefix="request")

    active_tab = request.GET.get("tab", "enquiry")
    if active_tab not in ("enquiry", "request"):
        active_tab = "enquiry"
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "enquiry":
            active_tab = "enquiry"
            enquiry_form = ContactInquiryForm(request.POST, prefix="enquiry")
            if enquiry_form.is_valid():
                enquiry_form.save()
                messages.success(request, _("Thank you. Your message has been received."))
                return redirect("/contact/?tab=enquiry")
        elif form_type == "request":
            active_tab = "request"
            request_form = ServiceRequestForm(request.POST, prefix="request")
            if request_form.is_valid():
                request_form.save()
                messages.success(request, _("Thank you. We have received your request."))
                return redirect("/contact/?tab=request")

    return render(request, "core/contact.html", {
        "enquiry_form": enquiry_form,
        "request_form": request_form,
        "active_tab": active_tab,
    })


def reviews(request):
    """Public customer reviews with photos."""
    testimonials = Testimonial.objects.filter(is_published=True).select_related("estate")
    return render(request, "core/reviews.html", {
        "testimonials": testimonials,
        "rating_average": testimonial_rating(),
        "testimonial_count": testimonials.count(),
        "results": results_snapshot(),
    })


def results(request):
    """Public 2025 results: weddings per month, guests and estates."""
    year = RESULTS_YEAR
    requested_year = request.GET.get("year", "")
    if requested_year.isdigit():
        year = int(requested_year)
    return render(request, "core/results.html", {
        "results": results_snapshot(year),
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
    })


@require_http_methods(["GET", "POST"])
def appointment(request):
    """Public appointment request form with a consultation explanation."""
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Thank you. Your appointment request has been received  -  "
            "our team will confirm the date and time by email within one business day.",
        )
        return redirect("core:appointment")
    return render(request, "core/appointment.html", {"form": form})


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import FieldDoesNotExist
from django.db import models as db_models
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.urls import reverse, reverse_lazy

from catalog.models import Vehicle, Estate
from .data_transfer import (
    export_field_names,
    export_file,
    format_from_filename,
    get_dataset,
    import_file,
    normalize_format,
)
from .forms import AppointmentForm, BookingForm, ContactInquiryForm, ServiceRequestForm, VehicleRentalForm
from .models import (
    Appointment,
    Booking,
    ContactInquiry,
    PaymentSchedule,
    ServiceRequest,
    Testimonial,
    VehicleRental,
    WeddingRecord,
)
from .notifications import mark_notifications_read


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "accounts:login"
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


# Extra columns shown by each dashboard list, after the record label and
# before the actions menu. Labels are lazy so they follow the active language.
LIST_COLUMNS = {
    "core.booking": [
        ("estate", gettext_lazy("Estate")),
        ("wedding_date", gettext_lazy("Wedding date")),
        ("guest_count", gettext_lazy("Guest count")),
        ("get_status_display", gettext_lazy("Status")),
        ("quoted_estate_total", gettext_lazy("Quoted total"), "€"),
    ],
    "core.servicerequest": [
        ("full_name", gettext_lazy("Full name")),
        ("get_event_type_display", gettext_lazy("Event type")),
        ("event_date", gettext_lazy("Event date")),
        ("get_destination_display", gettext_lazy("Destination")),
        ("guest_count", gettext_lazy("Guest count")),
    ],
    "core.contactinquiry": [
        ("full_name", gettext_lazy("Full name")),
        ("email", gettext_lazy("Email")),
        ("subject", gettext_lazy("Subject")),
        ("created_at", gettext_lazy("Created at")),
    ],
    "core.vehiclerental": [
        ("vehicle", gettext_lazy("Vehicle")),
        ("booking", gettext_lazy("Booking")),
        ("start_date", gettext_lazy("Start date")),
        ("end_date", gettext_lazy("End date")),
        ("amount_due", gettext_lazy("Amount due"), "€"),
        ("is_paid", gettext_lazy("Paid")),
    ],
    "core.paymentschedule": [
        ("booking", gettext_lazy("Booking")),
        ("deposit", gettext_lazy("Deposit"), "€"),
        ("installment_months", gettext_lazy("Installment months")),
        ("monthly_estimate", gettext_lazy("Estimated monthly installment"), "€"),
        ("approved", gettext_lazy("Approved")),
    ],
    "core.appointment": [
        ("full_name", gettext_lazy("Full name")),
        ("get_appointment_type_display", gettext_lazy("Appointment type")),
        ("preferred_date", gettext_lazy("Preferred date")),
        ("preferred_time", gettext_lazy("Preferred time")),
        ("get_status_display", gettext_lazy("Status")),
    ],
    "core.testimonial": [
        ("couple_names", gettext_lazy("Couple names")),
        ("estate", gettext_lazy("Estate")),
        ("rating", gettext_lazy("Rating")),
        ("is_published", gettext_lazy("Published")),
        ("position", gettext_lazy("Display order")),
    ],
    "core.weddingrecord": [
        ("reference", gettext_lazy("Reference")),
        ("estate", gettext_lazy("Estate")),
        ("get_country_display", gettext_lazy("Country")),
        ("wedding_date", gettext_lazy("Wedding date")),
        ("guest_count", gettext_lazy("Guest count")),
    ],
    "catalog.estate": [
        ("get_country_display", gettext_lazy("Country")),
        ("get_estate_type_display", gettext_lazy("Estate type")),
        ("region", gettext_lazy("Region")),
        ("city", gettext_lazy("City")),
        ("capacity", gettext_lazy("Capacity")),
        ("price_from", gettext_lazy("Price from"), "€"),
        ("is_published", gettext_lazy("Published")),
    ],
    "catalog.vehicle": [
        ("brand", gettext_lazy("Brand")),
        ("model", gettext_lazy("Model")),
        ("get_vehicle_type_display", gettext_lazy("Vehicle type")),
        ("daily_price", gettext_lazy("Daily price"), "€"),
        ("is_available", gettext_lazy("Available for rental")),
    ],
}


def _table_value(obj, name):
    """Return a display-friendly value for a dashboard table cell."""
    try:
        field = obj._meta.get_field(name)
    except FieldDoesNotExist:
        field = None

    value = getattr(obj, name, None)
    if field is not None and field.choices:
        display = getattr(obj, f"get_{name}_display", None)
        if display is not None:
            value = display
    if callable(value):
        value = value()
    if isinstance(value, bool):
        return _("Yes") if value else _("No")
    if value is None or value == "":
        return "—"
    return str(value)


BULK_BOOLEAN_ACTIONS = {
    "is_published": (
        gettext_lazy("Publish"),
        gettext_lazy("Unpublish"),
    ),
    "is_active": (
        gettext_lazy("Activate"),
        gettext_lazy("Deactivate"),
    ),
    "approved": (
        gettext_lazy("Approve"),
        gettext_lazy("Unapprove"),
    ),
    "is_paid": (
        gettext_lazy("Mark as paid"),
        gettext_lazy("Mark as unpaid"),
    ),
    "is_available": (
        gettext_lazy("Mark as available"),
        gettext_lazy("Mark as unavailable"),
    ),
}


def _bulk_actions(model):
    """Return bulk actions supported by the fields on ``model``."""
    fields = {field.name: field for field in model._meta.concrete_fields}
    actions = []
    for field_name, (true_label, false_label) in BULK_BOOLEAN_ACTIONS.items():
        field = fields.get(field_name)
        if not isinstance(field, db_models.BooleanField):
            continue
        actions.append({
            "value": f"set_true:{field_name}",
            "label": true_label,
        })
        actions.append({
            "value": f"set_false:{field_name}",
            "label": false_label,
        })
    actions.append({
        "value": "delete",
        "label": gettext_lazy("Delete selected"),
        "danger": True,
    })
    return actions


SEARCH_FIELD_TYPES = (db_models.CharField, db_models.TextField)


def _search_fields(model):
    return [
        field.name
        for field in model._meta.concrete_fields
        if isinstance(field, SEARCH_FIELD_TYPES)
    ]


def _list_filters(model):
    filters = []
    for field in model._meta.concrete_fields:
        if isinstance(field, db_models.BooleanField):
            options = [
                {"value": "true", "label": _("Yes")},
                {"value": "false", "label": _("No")},
            ]
        elif field.choices:
            options = [
                {"value": str(value), "label": label}
                for value, label in field.choices
            ]
        else:
            continue
        filters.append({
            "name": f"filter_{field.name}",
            "field": field.name,
            "label": field.verbose_name,
            "boolean": isinstance(field, db_models.BooleanField),
            "options": options,
        })
    return filters


class DashboardListView(StaffRequiredMixin, ListView):
    template_name = "core/dashboard_list.html"
    partial_template_name = "core/dashboard_list_results.html"
    context_object_name = "objects"
    model_name = ""
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""
    ordering = "pk"
    paginate_by = 24

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template_name]
        return [self.template_name]

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_query = self.request.GET.get("q", "").strip()
        if self.search_query:
            conditions = Q()
            for field_name in _search_fields(self.model):
                conditions |= Q(**{f"{field_name}__icontains": self.search_query})
            if self.search_query.isdigit():
                conditions |= Q(pk=int(self.search_query))
            queryset = queryset.filter(conditions)

        self.active_filters = {}
        for item in _list_filters(self.model):
            value = self.request.GET.get(item["name"], "")
            allowed = {str(option["value"]) for option in item["options"]}
            if not value or value not in allowed:
                continue
            queryset = queryset.filter(
                **{item["field"]: value == "true" if item["boolean"] else value}
            )
            self.active_filters[item["field"]] = value
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_key = self.model._meta.label_lower
        columns = LIST_COLUMNS.get(model_key, ())
        list_filters = _list_filters(self.model)
        for item in list_filters:
            for option in item["options"]:
                option["selected"] = (
                    getattr(self, "active_filters", {}).get(item["field"])
                    == str(option["value"])
                )
        rows = []
        for obj in context["objects"]:
            cells = []
            for spec in columns:
                name, label = spec[:2]
                prefix = spec[2] if len(spec) > 2 else ""
                value = _table_value(obj, name)
                cells.append({
                    "label": label,
                    "value": f"{prefix}{value}" if prefix and value != "—" else value,
                })
            rows.append({"object": obj, "cells": cells})

        context.update({
            "model_name": self.model_name,
            "model_key": model_key,
            "columns": [spec[1] for spec in columns],
            "rows": rows,
            "create_url_name": self.create_url_name,
            "update_url_name": self.update_url_name,
            "delete_url_name": self.delete_url_name,
            "import_url": reverse("core:dashboard-import", args=[model_key]),
            "export_url": reverse("core:dashboard-export", args=[model_key]),
            "bulk_action_url": reverse("core:dashboard-bulk", args=[model_key]),
            "bulk_actions": _bulk_actions(self.model),
            "search_query": getattr(self, "search_query", ""),
            "list_filters": list_filters,
            "has_filters": bool(getattr(self, "search_query", "") or getattr(self, "active_filters", {})),
            "per_page": context["paginator"].per_page if context.get("paginator") else self.paginate_by,
            "objects_in_view": len(context["page_obj"].object_list) if context.get("page_obj") else len(context["objects"]),
            "total_count": context["paginator"].count if context.get("paginator") else len(context["objects"]),
        })
        return context


class DashboardCreateView(StaffRequiredMixin, CreateView):
    template_name = "core/dashboard_form.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)


class DashboardUpdateView(StaffRequiredMixin, UpdateView):
    template_name = "core/dashboard_form.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)


class DashboardDeleteView(StaffRequiredMixin, DeleteView):
    template_name = "core/dashboard_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)


def _detail_fields(obj):
    """Build a display-friendly field list for the generic detail page."""
    fields = []
    for field in obj._meta.concrete_fields:
        if field.many_to_many:
            value = list(getattr(obj, field.name).all())
        elif field.is_relation:
            value = getattr(obj, field.name)
        else:
            value = field.value_from_object(obj)

        display = ""
        image_url = ""
        if value is None or value == "":
            display = ""
        elif isinstance(value, bool):
            display = _("Yes") if value else _("No")
        elif isinstance(value, (list, tuple)):
            display = ", ".join(str(item) for item in value)
        elif hasattr(value, "url") and hasattr(value, "name"):
            display = value.name
            if isinstance(field, db_models.ImageField) and value:
                try:
                    image_url = value.url
                except ValueError:
                    image_url = ""
        else:
            display = str(value)

        fields.append({
            "name": field.name,
            "label": field.verbose_name,
            "value": display,
            "image_url": image_url,
            "wide": isinstance(field, db_models.TextField) or field.name in {
                "description", "message", "needs", "quote", "notes",
            },
        })
    return fields


class DashboardDetailView(StaffRequiredMixin, View):
    """Generic read-only detail page shared by every dashboard list view."""

    template_name = "core/dashboard_detail.html"

    def get(self, request, model_key, pk):
        model, dataset = get_dataset(model_key)
        obj = get_object_or_404(model, pk=pk)
        url_base = dataset["list_url_name"].rsplit("-list", 1)[0]
        return render(request, self.template_name, {
            "object": obj,
            "model_name": dataset["label"],
            "fields": _detail_fields(obj),
            "list_url": reverse(dataset["list_url_name"]),
            "update_url": reverse(f"{url_base}-update", args=[obj.pk]),
            "delete_url": reverse(f"{url_base}-delete", args=[obj.pk]),
        })


class DashboardNotificationsMarkReadView(StaffRequiredMixin, View):
    """Mark all current dashboard notifications as read for this user."""

    def post(self, request):
        count = mark_notifications_read(request.user)
        if count:
            messages.success(
                request,
                ngettext(
                    "Marked %(count)s notification as read.",
                    "Marked %(count)s notifications as read.",
                    count,
                ) % {"count": count},
            )
        else:
            messages.info(request, _("All notifications are already read."))

        next_url = request.POST.get("next", "")
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = reverse("core:dashboard")
        return redirect(next_url)


class DashboardExportView(StaffRequiredMixin, View):
    """Download the current dashboard list view's records as CSV or XLSX."""

    def get(self, request, model_key):
        model, dataset = get_dataset(model_key)
        file_format = normalize_format(request.GET.get("format")) or "csv"
        return export_file(model, export_field_names(model), dataset["label"], file_format)


class DashboardBulkActionView(StaffRequiredMixin, View):
    """Apply a shared action to one or more records from a dashboard list."""

    def post(self, request, model_key):
        model, dataset = get_dataset(model_key)
        list_url = reverse(dataset["list_url_name"])

        selected_ids = []
        for value in request.POST.getlist("selected_ids"):
            try:
                selected_ids.append(int(value))
            except (TypeError, ValueError):
                continue

        if not selected_ids:
            messages.error(request, _("Please select at least one record."))
            return redirect(list_url)

        action = request.POST.get("action", "")
        allowed_actions = {item["value"] for item in _bulk_actions(model)}
        if action not in allowed_actions:
            messages.error(request, _("Please choose a valid action."))
            return redirect(list_url)

        queryset = model.objects.filter(pk__in=selected_ids)
        count = queryset.count()
        if not count:
            messages.error(request, _("The selected records no longer exist."))
            return redirect(list_url)

        if action == "delete":
            queryset.delete()
            message = ngettext(
                "Deleted %(count)s record.",
                "Deleted %(count)s records.",
                count,
            ) % {"count": count}
        else:
            operation, field_name = action.split(":", 1)
            queryset.update(**{field_name: operation == "set_true"})
            message = ngettext(
                "Updated %(count)s record.",
                "Updated %(count)s records.",
                count,
            ) % {"count": count}

        messages.success(request, message)
        return redirect(list_url)


class DashboardImportView(StaffRequiredMixin, View):
    """Upload a CSV/XLSX file to create or update dashboard records."""

    template_name = "core/dashboard_import.html"
    formats = [("csv", "CSV"), ("xlsx", "XLSX")]

    def _context(self, model_key, model, dataset, selected_format="csv", errors=None):
        return {
            "model_name": dataset["label"],
            "fields": export_field_names(model),
            "formats": self.formats,
            "selected_format": selected_format,
            "import_url": reverse("core:dashboard-import", args=[model_key]),
            "list_url": reverse(dataset["list_url_name"]),
            "errors": errors or [],
        }

    def get(self, request, model_key):
        model, dataset = get_dataset(model_key)
        return render(request, self.template_name, self._context(model_key, model, dataset))

    def post(self, request, model_key):
        model, dataset = get_dataset(model_key)
        upload = request.FILES.get("data_file") or request.FILES.get("csv_file")

        file_format = normalize_format(request.POST.get("format"), default=None)
        if file_format is None:
            file_format = format_from_filename(upload.name if upload else "", "csv")
        context = self._context(model_key, model, dataset, file_format)

        if not upload:
            context["errors"] = [_("Please choose a file.")]
        elif upload.size > 5 * 1024 * 1024:
            context["errors"] = [_("The file must be smaller than 5 MB.")]
        else:
            imported, errors = import_file(
                model, export_field_names(model), upload, file_format
            )
            if errors:
                context["errors"] = errors
            else:
                messages.success(
                    request,
                    ngettext(
                        "Imported %(count)s record.",
                        "Imported %(count)s records.",
                        imported,
                    ) % {"count": imported},
                )
                return redirect(dataset["list_url_name"])

        return render(request, self.template_name, context)


class BookingListView(DashboardListView):
    model = Booking
    model_name = "Booking"
    create_url_name = "core:booking-create"
    update_url_name = "core:booking-update"
    delete_url_name = "core:booking-delete"

class BookingCreateView(DashboardCreateView):
    model = Booking
    form_class = BookingForm
    fields = None
    success_url_name = "core:booking-list"

class BookingUpdateView(DashboardUpdateView):
    model = Booking
    form_class = BookingForm
    fields = None
    success_url_name = "core:booking-list"

class BookingDeleteView(DashboardDeleteView):
    model = Booking
    success_url_name = "core:booking-list"


class ServiceRequestListView(DashboardListView):
    model = ServiceRequest
    model_name = "Service Request"
    create_url_name = "core:service-request-create"
    update_url_name = "core:service-request-update"
    delete_url_name = "core:service-request-delete"

class ServiceRequestCreateView(DashboardCreateView):
    model = ServiceRequest
    form_class = ServiceRequestForm
    fields = None
    success_url_name = "core:service-request-list"

class ServiceRequestUpdateView(DashboardUpdateView):
    model = ServiceRequest
    form_class = ServiceRequestForm
    fields = None
    success_url_name = "core:service-request-list"

class ServiceRequestDeleteView(DashboardDeleteView):
    model = ServiceRequest
    success_url_name = "core:service-request-list"


class ContactInquiryListView(DashboardListView):
    model = ContactInquiry
    model_name = "Contact Inquiry"
    create_url_name = "core:contact-inquiry-create"
    update_url_name = "core:contact-inquiry-update"
    delete_url_name = "core:contact-inquiry-delete"

class ContactInquiryCreateView(DashboardCreateView):
    model = ContactInquiry
    form_class = ContactInquiryForm
    fields = None
    success_url_name = "core:contact-inquiry-list"

class ContactInquiryUpdateView(DashboardUpdateView):
    model = ContactInquiry
    form_class = ContactInquiryForm
    fields = None
    success_url_name = "core:contact-inquiry-list"

class ContactInquiryDeleteView(DashboardDeleteView):
    model = ContactInquiry
    success_url_name = "core:contact-inquiry-list"


class VehicleRentalListView(DashboardListView):
    model = VehicleRental
    model_name = "Vehicle Rental"
    create_url_name = "core:vehicle-rental-create"
    update_url_name = "core:vehicle-rental-update"
    delete_url_name = "core:vehicle-rental-delete"

class VehicleRentalCreateView(DashboardCreateView):
    model = VehicleRental
    form_class = VehicleRentalForm
    fields = None
    success_url_name = "core:vehicle-rental-list"

class VehicleRentalUpdateView(DashboardUpdateView):
    model = VehicleRental
    form_class = VehicleRentalForm
    fields = None
    success_url_name = "core:vehicle-rental-list"

class VehicleRentalDeleteView(DashboardDeleteView):
    model = VehicleRental
    success_url_name = "core:vehicle-rental-list"


class PaymentScheduleListView(DashboardListView):
    model = PaymentSchedule
    model_name = "Payment Schedule"
    create_url_name = "core:payment-schedule-create"
    update_url_name = "core:payment-schedule-update"
    delete_url_name = "core:payment-schedule-delete"

class PaymentScheduleCreateView(DashboardCreateView):
    model = PaymentSchedule
    success_url_name = "core:payment-schedule-list"

class PaymentScheduleUpdateView(DashboardUpdateView):
    model = PaymentSchedule
    success_url_name = "core:payment-schedule-list"

class PaymentScheduleDeleteView(DashboardDeleteView):
    model = PaymentSchedule
    success_url_name = "core:payment-schedule-list"


class AppointmentListView(DashboardListView):
    model = Appointment
    model_name = "Appointment"
    create_url_name = "core:appointment-record-create"
    update_url_name = "core:appointment-record-update"
    delete_url_name = "core:appointment-record-delete"


class AppointmentCreateView(DashboardCreateView):
    model = Appointment
    form_class = AppointmentForm
    fields = None
    success_url_name = "core:appointment-record-list"


class AppointmentUpdateView(DashboardUpdateView):
    model = Appointment
    form_class = AppointmentForm
    fields = None
    success_url_name = "core:appointment-record-list"


class AppointmentDeleteView(DashboardDeleteView):
    model = Appointment
    success_url_name = "core:appointment-record-list"


class TestimonialListView(DashboardListView):
    model = Testimonial
    model_name = "Testimonial"
    create_url_name = "core:testimonial-create"
    update_url_name = "core:testimonial-update"
    delete_url_name = "core:testimonial-delete"


class TestimonialCreateView(DashboardCreateView):
    model = Testimonial
    success_url_name = "core:testimonial-list"


class TestimonialUpdateView(DashboardUpdateView):
    model = Testimonial
    success_url_name = "core:testimonial-list"


class TestimonialDeleteView(DashboardDeleteView):
    model = Testimonial
    success_url_name = "core:testimonial-list"


class WeddingRecordListView(DashboardListView):
    model = WeddingRecord
    model_name = "Wedding Record"
    create_url_name = "core:wedding-record-create"
    update_url_name = "core:wedding-record-update"
    delete_url_name = "core:wedding-record-delete"


class WeddingRecordCreateView(DashboardCreateView):
    model = WeddingRecord
    success_url_name = "core:wedding-record-list"


class WeddingRecordUpdateView(DashboardUpdateView):
    model = WeddingRecord
    success_url_name = "core:wedding-record-list"


class WeddingRecordDeleteView(DashboardDeleteView):
    model = WeddingRecord
    success_url_name = "core:wedding-record-list"


class EstateListView(DashboardListView):
    model = Estate
    model_name = "Estate"
    create_url_name = "core:estate-create"
    update_url_name = "core:estate-update"
    delete_url_name = "core:estate-delete"

class EstateCreateView(DashboardCreateView):
    model = Estate
    fields = "__all__"
    success_url_name = "core:estate-list"

class EstateUpdateView(DashboardUpdateView):
    model = Estate
    fields = "__all__"
    success_url_name = "core:estate-list"

class EstateDeleteView(DashboardDeleteView):
    model = Estate
    success_url_name = "core:estate-list"


class VehicleListView(DashboardListView):
    model = Vehicle
    model_name = "Vehicle"
    create_url_name = "core:vehicle-create"
    update_url_name = "core:vehicle-update"
    delete_url_name = "core:vehicle-delete"

class VehicleCreateView(DashboardCreateView):
    model = Vehicle
    fields = "__all__"
    success_url_name = "core:vehicle-list"

class VehicleUpdateView(DashboardUpdateView):
    model = Vehicle
    fields = "__all__"
    success_url_name = "core:vehicle-list"

class VehicleDeleteView(DashboardDeleteView):
    model = Vehicle
    success_url_name = "core:vehicle-list"


from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url="accounts:login")
def dashboard(request):
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    from django.shortcuts import render
    models = [
        {"name": "Booking", "url": "core:booking-list", "count": Booking.objects.count()},
        {"name": "Service Request", "url": "core:service-request-list", "count": ServiceRequest.objects.count()},
        {"name": "Contact Inquiry", "url": "core:contact-inquiry-list", "count": ContactInquiry.objects.count()},
        {"name": "Appointment", "url": "core:appointment-record-list", "count": Appointment.objects.count()},
        {"name": "Testimonial", "url": "core:testimonial-list", "count": Testimonial.objects.count()},
        {"name": "Wedding Record", "url": "core:wedding-record-list", "count": WeddingRecord.objects.count()},
        {"name": "Vehicle Rental", "url": "core:vehicle-rental-list", "count": VehicleRental.objects.count()},
        {"name": "Payment Schedule", "url": "core:payment-schedule-list", "count": PaymentSchedule.objects.count()},
        {"name": "Estate", "url": "core:estate-list", "count": Estate.objects.count()},
        {"name": "Vehicle", "url": "core:vehicle-list", "count": Vehicle.objects.count()},
    ]
    return render(request, "core/dashboard.html", {"models": models})


from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.formats import date_format


def _choice_label(value, labels):
    """Return a display label for a grouped choice value."""
    if value in (None, ""):
        return str(_("Not specified"))
    return str(labels.get(value, value))


def _distribution(queryset, field, labels=None):
    """Return aligned labels/totals for a simple ``values`` aggregation."""
    rows = list(queryset.values(field).annotate(total=Count("id")).order_by("-total"))
    return (
        [_choice_label(row[field], labels or {}) for row in rows],
        [row["total"] for row in rows],
    )


def _chart(chart_id, title, subtitle, chart_type, labels, data, **options):
    """Build the serialisable configuration consumed by the statistics page."""
    return {
        "id": chart_id,
        "title": str(title),
        "subtitle": str(subtitle),
        "type": chart_type,
        "labels": labels,
        "data": data,
        "has_data": bool(data) and any(total > 0 for total in data),
        "dataset_label": str(options.get("dataset_label", _("Total"))),
        "empty_message": str(options.get("empty_message", _("No data available yet."))),
        "color": options.get("color", "#243b32"),
        "horizontal": options.get("horizontal", False),
        "icon": options.get("icon", "fa-chart-simple"),
    }


class StatisticsView(StaffRequiredMixin, ListView):
    template_name = "core/statistics.html"
    context_object_name = "objects"

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        country_labels = dict(Estate.COUNTRY_CHOICES)
        event_labels = dict(ServiceRequest.EVENT_CHOICES)
        destination_labels = dict(ServiceRequest.DESTINATION_CHOICES)
        booking_status_labels = dict(Booking.Status.choices)
        appointment_type_labels = dict(Appointment.Kind.choices)
        category_labels = dict(Vehicle.Category.choices)

        booking_count = Booking.objects.count()
        request_count = ServiceRequest.objects.count()
        inquiry_count = ContactInquiry.objects.count()
        estate_count = Estate.objects.count()
        vehicle_count = Vehicle.objects.count()
        appointment_count = Appointment.objects.count()
        payments_approved = PaymentSchedule.objects.filter(approved=True).count()
        payments_pending = PaymentSchedule.objects.filter(approved=False).count()

        bookings_labels, bookings_data = _distribution(Booking.objects.all(), "estate__name")
        booking_status_labels, booking_status_data = _distribution(
            Booking.objects.all(), "status", booking_status_labels
        )
        requests_type_labels, requests_type_data = _distribution(
            ServiceRequest.objects.all(), "event_type", event_labels
        )
        requests_destination_labels, requests_destination_data = _distribution(
            ServiceRequest.objects.all(), "destination", destination_labels
        )
        rentals_labels, rentals_data = _distribution(VehicleRental.objects.all(), "vehicle__name")

        inquiry_rows = list(
            ContactInquiry.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )
        inquiry_labels = [
            date_format(row["month"], "M Y") if row["month"] else str(_("Not specified"))
            for row in inquiry_rows
        ]
        inquiry_data = [row["total"] for row in inquiry_rows]

        vehicles_labels, vehicles_data = _distribution(
            Vehicle.objects.all(), "category", category_labels
        )
        estates_labels, estates_data = _distribution(Estate.objects.all(), "country", country_labels)
        appointments_labels, appointments_data = _distribution(
            Appointment.objects.all(), "appointment_type", appointment_type_labels
        )

        summary = [
            {
                "label": str(_("Bookings")),
                "value": booking_count,
                "description": str(_("Estate enquiries")),
                "icon": "fa-solid fa-building",
                "url": reverse("core:booking-list"),
            },
            {
                "label": str(_("Service requests")),
                "value": request_count,
                "description": str(_("Event planning requests")),
                "icon": "fa-solid fa-clipboard-list",
                "url": reverse("core:service-request-list"),
            },
            {
                "label": str(_("Inquiries")),
                "value": inquiry_count,
                "description": str(_("Contact messages")),
                "icon": "fa-solid fa-envelope",
                "url": reverse("core:contact-inquiry-list"),
            },
            {
                "label": str(_("Estates")),
                "value": estate_count,
                "description": str(_("Properties in the collection")),
                "icon": "fa-solid fa-map-location-dot",
                "url": reverse("core:estate-list"),
            },
            {
                "label": str(_("Vehicles")),
                "value": vehicle_count,
                "description": str(_("Available fleet")),
                "icon": "fa-solid fa-car",
                "url": reverse("core:vehicle-list"),
            },
            {
                "label": str(_("Appointments")),
                "value": appointment_count,
                "description": str(_("Calls and estate visits")),
                "icon": "fa-solid fa-calendar-day",
                "url": reverse("core:appointment-record-list"),
            },
        ]

        chart_sections = [
            {
                "id": "bookings-inquiries",
                "title": str(_("Bookings and inquiries")),
                "description": str(_("Where demand comes from and how conversations trend.")),
                "icon": "fa-solid fa-calendar-check",
                "charts": [
                    _chart(
                        "bookings-by-estate",
                        _("Bookings by estate"),
                        _("Estates with the most bookings"),
                        "bar",
                        bookings_labels,
                        bookings_data,
                        dataset_label=_("Bookings"),
                        empty_message=_("No bookings have been recorded yet."),
                        horizontal=True,
                        icon="fa-solid fa-building",
                    ),
                    _chart(
                        "inquiries-by-month",
                        _("Inquiries over time"),
                        _("Contact inquiries by month"),
                        "line",
                        inquiry_labels,
                        inquiry_data,
                        dataset_label=_("Inquiries"),
                        empty_message=_("No inquiries have been recorded yet."),
                        color="#a58a5a",
                        icon="fa-solid fa-envelope",
                    ),
                ],
            },
            {
                "id": "service-requests",
                "title": str(_("Service requests")),
                "description": str(_("Event types and preferred destinations.")),
                "icon": "fa-solid fa-clipboard-list",
                "charts": [
                    _chart(
                        "requests-by-type",
                        _("Requests by event type"),
                        _("Services requested by celebration type"),
                        "doughnut",
                        requests_type_labels,
                        requests_type_data,
                        dataset_label=_("Requests"),
                        empty_message=_("No service requests have been recorded yet."),
                        icon="fa-solid fa-chart-pie",
                    ),
                    _chart(
                        "requests-by-destination",
                        _("Requests by destination"),
                        _("Preferred countries"),
                        "bar",
                        requests_destination_labels,
                        requests_destination_data,
                        dataset_label=_("Requests"),
                        empty_message=_("No service requests have been recorded yet."),
                        color="#a58a5a",
                        icon="fa-solid fa-globe",
                    ),
                ],
            },
            {
                "id": "fleet-rentals",
                "title": str(_("Fleet and rentals")),
                "description": str(_("Vehicle mix and rental demand.")),
                "icon": "fa-solid fa-car",
                "charts": [
                    _chart(
                        "vehicles-by-category",
                        _("Vehicles by category"),
                        _("Current fleet composition"),
                        "doughnut",
                        vehicles_labels,
                        vehicles_data,
                        dataset_label=_("Vehicles"),
                        empty_message=_("No vehicles have been added yet."),
                        icon="fa-solid fa-car",
                    ),
                    _chart(
                        "rentals-by-vehicle",
                        _("Rentals by vehicle"),
                        _("Most rented vehicles"),
                        "bar",
                        rentals_labels,
                        rentals_data,
                        dataset_label=_("Rentals"),
                        empty_message=_("No vehicle rentals have been recorded yet."),
                        horizontal=True,
                        icon="fa-solid fa-car-side",
                    ),
                ],
            },
            {
                "id": "estates-status",
                "title": str(_("Estates and booking status")),
                "description": str(_("Catalog coverage and the current booking pipeline.")),
                "icon": "fa-solid fa-map-location-dot",
                "charts": [
                    _chart(
                        "estates-by-country",
                        _("Estates by country"),
                        _("Properties in the collection"),
                        "doughnut",
                        estates_labels,
                        estates_data,
                        dataset_label=_("Estates"),
                        empty_message=_("No estates have been added yet."),
                        icon="fa-solid fa-chart-pie",
                    ),
                    _chart(
                        "bookings-by-status",
                        _("Bookings by status"),
                        _("Current booking pipeline"),
                        "bar",
                        booking_status_labels,
                        booking_status_data,
                        dataset_label=_("Bookings"),
                        empty_message=_("No bookings have been recorded yet."),
                        color="#a58a5a",
                        icon="fa-solid fa-list-check",
                    ),
                ],
            },
            {
                "id": "payments-appointments",
                "title": str(_("Payments and appointments")),
                "description": str(_("Approvals and consultation requests.")),
                "icon": "fa-solid fa-credit-card",
                "charts": [
                    _chart(
                        "payment-status",
                        _("Payment schedules"),
                        _("Approved versus pending"),
                        "doughnut",
                        [str(_("Approved")), str(_("Pending"))],
                        [payments_approved, payments_pending],
                        dataset_label=_("Schedules"),
                        empty_message=_("No payment schedules have been recorded yet."),
                        icon="fa-solid fa-credit-card",
                    ),
                    _chart(
                        "appointments-by-type",
                        _("Appointments by type"),
                        _("Calls and estate visits"),
                        "bar",
                        appointments_labels,
                        appointments_data,
                        dataset_label=_("Appointments"),
                        empty_message=_("No appointments have been recorded yet."),
                        icon="fa-solid fa-calendar-day",
                    ),
                ],
            },
        ]

        context.update({
            "summary": summary,
            "chart_sections": chart_sections,
            "statistics_data": {"summary": summary, "chart_sections": chart_sections},
        })
        return context


def statistics(request):
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    view = StatisticsView.as_view()
    return view(request)