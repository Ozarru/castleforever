from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path("venues/<slug:slug>/enquire/", views.booking_enquiry, name="booking-enquiry"),
    path("needs/", views.needs, name="needs"),
    path("contact/", views.contact, name="contact"),
    path("inquiry/", views.contact, name="inquiry"),
    path("enquire/", views.contact, name="enquire"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/statistics/", views.StatisticsView.as_view(), name="statistics"),

    path("dashboard/bookings/", views.BookingListView.as_view(), name="booking-list"),
    path("dashboard/bookings/create/", views.BookingCreateView.as_view(), name="booking-create"),
    path("dashboard/bookings/<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking-update"),
    path("dashboard/bookings/<int:pk>/delete/", views.BookingDeleteView.as_view(), name="booking-delete"),

    path("dashboard/service-requests/", views.ServiceRequestListView.as_view(), name="service-request-list"),
    path("dashboard/service-requests/create/", views.ServiceRequestCreateView.as_view(), name="service-request-create"),
    path("dashboard/service-requests/<int:pk>/edit/", views.ServiceRequestUpdateView.as_view(), name="service-request-update"),
    path("dashboard/service-requests/<int:pk>/delete/", views.ServiceRequestDeleteView.as_view(), name="service-request-delete"),

    path("dashboard/contact-inquiries/", views.ContactInquiryListView.as_view(), name="contact-inquiry-list"),
    path("dashboard/contact-inquiries/create/", views.ContactInquiryCreateView.as_view(), name="contact-inquiry-create"),
    path("dashboard/contact-inquiries/<int:pk>/edit/", views.ContactInquiryUpdateView.as_view(), name="contact-inquiry-update"),
    path("dashboard/contact-inquiries/<int:pk>/delete/", views.ContactInquiryDeleteView.as_view(), name="contact-inquiry-delete"),

    path("dashboard/vehicle-rentals/", views.VehicleRentalListView.as_view(), name="vehicle-rental-list"),
    path("dashboard/vehicle-rentals/create/", views.VehicleRentalCreateView.as_view(), name="vehicle-rental-create"),
    path("dashboard/vehicle-rentals/<int:pk>/edit/", views.VehicleRentalUpdateView.as_view(), name="vehicle-rental-update"),
    path("dashboard/vehicle-rentals/<int:pk>/delete/", views.VehicleRentalDeleteView.as_view(), name="vehicle-rental-delete"),

    path("dashboard/payment-schedules/", views.PaymentScheduleListView.as_view(), name="payment-schedule-list"),
    path("dashboard/payment-schedules/create/", views.PaymentScheduleCreateView.as_view(), name="payment-schedule-create"),
    path("dashboard/payment-schedules/<int:pk>/edit/", views.PaymentScheduleUpdateView.as_view(), name="payment-schedule-update"),
    path("dashboard/payment-schedules/<int:pk>/delete/", views.PaymentScheduleDeleteView.as_view(), name="payment-schedule-delete"),

    path("dashboard/venues/", views.VenueListView.as_view(), name="venue-list"),
    path("dashboard/venues/create/", views.VenueCreateView.as_view(), name="venue-create"),
    path("dashboard/venues/<int:pk>/edit/", views.VenueUpdateView.as_view(), name="venue-update"),
    path("dashboard/venues/<int:pk>/delete/", views.VenueDeleteView.as_view(), name="venue-delete"),

    path("dashboard/vehicles/", views.VehicleListView.as_view(), name="vehicle-list"),
    path("dashboard/vehicles/create/", views.VehicleCreateView.as_view(), name="vehicle-create"),
    path("dashboard/vehicles/<int:pk>/edit/", views.VehicleUpdateView.as_view(), name="vehicle-update"),
    path("dashboard/vehicles/<int:pk>/delete/", views.VehicleDeleteView.as_view(), name="vehicle-delete"),
]