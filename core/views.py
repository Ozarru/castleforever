from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from catalog.models import Venue
from .forms import BookingEnquiryForm, ContactInquiryForm, ServiceRequestForm
from .models import ContactInquiry, ServiceRequest


@require_http_methods(["GET", "POST"])
def booking_enquiry(request, slug):
    venue = get_object_or_404(Venue, slug=slug, is_published=True)
    form = BookingEnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.venue = venue
        booking.quoted_venue_total = venue.price_from
        if request.user.is_authenticated:
            booking.user = request.user
        booking.save()
        messages.success(request, "Your enquiry has been received. We will contact you about availability.")
        return redirect(venue.get_absolute_url())
    return render(request, "core/enquiry.html", {"form": form, "venue": venue})


@require_http_methods(["GET", "POST"])
def needs(request):
    return redirect("/contact/?tab=request")


@require_http_methods(["GET", "POST"])
def contact(request):
    enquiry_form = ContactInquiryForm(request.POST or None, prefix="enquiry") if (request.method == "POST" and request.POST.get("form_type") == "enquiry") else ContactInquiryForm(prefix="enquiry")
    request_form = ServiceRequestForm(request.POST or None, prefix="request") if (request.method == "POST" and request.POST.get("form_type") == "request") else ServiceRequestForm(prefix="request")

    active_tab = request.GET.get("tab", "enquiry")
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "enquiry":
            active_tab = "enquiry"
            enquiry_form = ContactInquiryForm(request.POST, prefix="enquiry")
            if enquiry_form.is_valid():
                enquiry_form.save()
                messages.success(request, "Thank you. Your message has been received.")
                return redirect("/contact/?tab=enquiry")
        elif form_type == "request":
            active_tab = "request"
            request_form = ServiceRequestForm(request.POST, prefix="request")
            if request_form.is_valid():
                request_form.save()
                messages.success(request, "Thank you. We have received your request.")
                return redirect("/contact/?tab=request")

    return render(request, "core/contact.html", {
        "enquiry_form": enquiry_form,
        "request_form": request_form,
        "active_tab": active_tab,
    })


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy

from catalog.models import Vehicle, Venue
from .forms import BookingForm, ContactInquiryForm, ServiceRequestForm, VehicleRentalForm
from .models import Booking, ContactInquiry, PaymentSchedule, ServiceRequest, VehicleRental


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "accounts:login"
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class DashboardListView(StaffRequiredMixin, ListView):
    template_name = "core/dashboard_list.html"
    context_object_name = "objects"
    model_name = ""
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model_name
        context["create_url_name"] = self.create_url_name
        context["update_url_name"] = self.update_url_name
        context["delete_url_name"] = self.delete_url_name
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


class VenueListView(DashboardListView):
    model = Venue
    model_name = "Venue"
    create_url_name = "core:venue-create"
    update_url_name = "core:venue-update"
    delete_url_name = "core:venue-delete"

class VenueCreateView(DashboardCreateView):
    model = Venue
    fields = "__all__"
    success_url_name = "core:venue-list"

class VenueUpdateView(DashboardUpdateView):
    model = Venue
    fields = "__all__"
    success_url_name = "core:venue-list"

class VenueDeleteView(DashboardDeleteView):
    model = Venue
    success_url_name = "core:venue-list"


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
        {"name": "Vehicle Rental", "url": "core:vehicle-rental-list", "count": VehicleRental.objects.count()},
        {"name": "Payment Schedule", "url": "core:payment-schedule-list", "count": PaymentSchedule.objects.count()},
        {"name": "Venue", "url": "core:venue-list", "count": Venue.objects.count()},
        {"name": "Vehicle", "url": "core:vehicle-list", "count": Vehicle.objects.count()},
    ]
    return render(request, "core/dashboard.html", {"models": models})


import json
from django.db.models import Count
from django.db.models.functions import TruncMonth


class StatisticsView(StaffRequiredMixin, ListView):
    template_name = "core/statistics.html"
    context_object_name = "objects"

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bookings_by_venue = list(
            Booking.objects.values("venue__name").annotate(total=Count("id")).order_by("-total")
        )
        requests_by_type = list(
            ServiceRequest.objects.values("event_type").annotate(total=Count("id")).order_by("-total")
        )
        requests_by_destination = list(
            ServiceRequest.objects.values("destination").annotate(total=Count("id")).order_by("-total")
        )
        inquiries_by_month = list(
            ContactInquiry.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )
        vehicles_by_category = list(
            Vehicle.objects.values("category").annotate(total=Count("id")).order_by("-total")
        )
        venues_by_country = list(
            Venue.objects.values("country").annotate(total=Count("id")).order_by("-total")
        )
        rentals_by_vehicle = list(
            VehicleRental.objects.values("vehicle__name").annotate(total=Count("id")).order_by("-total")
        )
        payments_approved = PaymentSchedule.objects.filter(approved=True).count()
        payments_pending = PaymentSchedule.objects.filter(approved=False).count()

        context.update({
            "bookings_by_venue_labels": json.dumps([x["venue__name"] for x in bookings_by_venue]),
            "bookings_by_venue_data": json.dumps([x["total"] for x in bookings_by_venue]),
            "requests_by_type_labels": json.dumps([x["event_type"] for x in requests_by_type]),
            "requests_by_type_data": json.dumps([x["total"] for x in requests_by_type]),
            "requests_by_destination_labels": json.dumps([x["destination"] for x in requests_by_destination]),
            "requests_by_destination_data": json.dumps([x["total"] for x in requests_by_destination]),
            "inquiries_month_labels": json.dumps([x["month"].strftime("%Y-%m") if x["month"] else "" for x in inquiries_by_month]),
            "inquiries_month_data": json.dumps([x["total"] for x in inquiries_by_month]),
            "vehicles_category_labels": json.dumps([x["category"] for x in vehicles_by_category]),
            "vehicles_category_data": json.dumps([x["total"] for x in vehicles_by_category]),
            "venues_country_labels": json.dumps([x["country"] for x in venues_by_country]),
            "venues_country_data": json.dumps([x["total"] for x in venues_by_country]),
            "rentals_vehicle_labels": json.dumps([x["vehicle__name"] for x in rentals_by_vehicle]),
            "rentals_vehicle_data": json.dumps([x["total"] for x in rentals_by_vehicle]),
            "payments_approved": payments_approved,
            "payments_pending": payments_pending,
        })
        return context


def statistics(request):
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    view = StatisticsView.as_view()
    return view(request)