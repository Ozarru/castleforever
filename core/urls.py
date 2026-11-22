from django.urls import path
from . import views
from .permissions import staff_required


def dashboard_path(route, view, name=None, **kwargs):
    """Dashboard route that cannot be reached by anonymous or non-staff users."""
    return path(route, staff_required(view), name=name, **kwargs)


app_name = "core"
urlpatterns = [
    path("estates/<slug:slug>/enquire/", views.booking_enquiry, name="booking-enquiry"),
    path("needs/", views.needs, name="needs"),
    path("contact/", views.contact, name="contact"),
    path("inquiry/", views.contact, name="inquiry"),
    path("enquire/", views.contact, name="enquire"),
    path("reviews/", views.reviews, name="reviews"),
    path("testimonials/", views.reviews, name="testimonials"),
    path("results/", views.results, name="results"),
    path("2025-results/", views.results, name="results-2025"),
    path("appointment/", views.appointment, name="appointment"),
    path("book-a-call/", views.appointment, name="book-a-call"),
    dashboard_path("dashboard/", views.dashboard, name="dashboard"),
    dashboard_path("dashboard/statistics/", views.StatisticsView.as_view(), name="statistics"),
    dashboard_path("dashboard/users/", views.DashboardUserListView.as_view(), name="user-list"),
    dashboard_path("dashboard/users/create/", views.DashboardUserCreateView.as_view(), name="user-create"),
    dashboard_path("dashboard/users/<int:pk>/", views.DashboardUserDetailView.as_view(), name="user-detail"),
    dashboard_path("dashboard/users/<int:pk>/edit/", views.DashboardUserUpdateView.as_view(), name="user-update"),
    dashboard_path("dashboard/users/<int:pk>/delete/", views.DashboardUserDeleteView.as_view(), name="user-delete"),
    dashboard_path("dashboard/detail/<str:model_key>/<int:pk>/", views.DashboardDetailView.as_view(), name="dashboard-detail"),
    dashboard_path("dashboard/notifications/read/", views.DashboardNotificationsMarkReadView.as_view(), name="notifications-mark-read"),

    dashboard_path("dashboard/data/<str:model_key>/bulk/", views.DashboardBulkActionView.as_view(), name="dashboard-bulk"),
    dashboard_path("dashboard/data/<str:model_key>/export/", views.DashboardExportView.as_view(), name="dashboard-export"),
    dashboard_path("dashboard/data/<str:model_key>/import/", views.DashboardImportView.as_view(), name="dashboard-import"),

    dashboard_path("dashboard/bookings/", views.BookingListView.as_view(), name="booking-list"),
    dashboard_path("dashboard/bookings/create/", views.BookingCreateView.as_view(), name="booking-create"),
    dashboard_path("dashboard/bookings/<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking-update"),
    dashboard_path("dashboard/bookings/<int:pk>/delete/", views.BookingDeleteView.as_view(), name="booking-delete"),

    dashboard_path("dashboard/service-requests/", views.ServiceRequestListView.as_view(), name="service-request-list"),
    dashboard_path("dashboard/service-requests/create/", views.ServiceRequestCreateView.as_view(), name="service-request-create"),
    dashboard_path("dashboard/service-requests/<int:pk>/edit/", views.ServiceRequestUpdateView.as_view(), name="service-request-update"),
    dashboard_path("dashboard/service-requests/<int:pk>/delete/", views.ServiceRequestDeleteView.as_view(), name="service-request-delete"),

    dashboard_path("dashboard/contact-inquiries/", views.ContactInquiryListView.as_view(), name="contact-inquiry-list"),
    dashboard_path("dashboard/contact-inquiries/create/", views.ContactInquiryCreateView.as_view(), name="contact-inquiry-create"),
    dashboard_path("dashboard/contact-inquiries/<int:pk>/edit/", views.ContactInquiryUpdateView.as_view(), name="contact-inquiry-update"),
    dashboard_path("dashboard/contact-inquiries/<int:pk>/delete/", views.ContactInquiryDeleteView.as_view(), name="contact-inquiry-delete"),

    dashboard_path("dashboard/vehicle-rentals/", views.VehicleRentalListView.as_view(), name="vehicle-rental-list"),
    dashboard_path("dashboard/vehicle-rentals/create/", views.VehicleRentalCreateView.as_view(), name="vehicle-rental-create"),
    dashboard_path("dashboard/vehicle-rentals/<int:pk>/edit/", views.VehicleRentalUpdateView.as_view(), name="vehicle-rental-update"),
    dashboard_path("dashboard/vehicle-rentals/<int:pk>/delete/", views.VehicleRentalDeleteView.as_view(), name="vehicle-rental-delete"),

    dashboard_path("dashboard/payment-schedules/", views.PaymentScheduleListView.as_view(), name="payment-schedule-list"),
    dashboard_path("dashboard/payment-schedules/create/", views.PaymentScheduleCreateView.as_view(), name="payment-schedule-create"),
    dashboard_path("dashboard/payment-schedules/<int:pk>/edit/", views.PaymentScheduleUpdateView.as_view(), name="payment-schedule-update"),
    dashboard_path("dashboard/payment-schedules/<int:pk>/delete/", views.PaymentScheduleDeleteView.as_view(), name="payment-schedule-delete"),

    dashboard_path("dashboard/appointments/", views.AppointmentListView.as_view(), name="appointment-record-list"),
    dashboard_path("dashboard/appointments/create/", views.AppointmentCreateView.as_view(), name="appointment-record-create"),
    dashboard_path("dashboard/appointments/<int:pk>/edit/", views.AppointmentUpdateView.as_view(), name="appointment-record-update"),
    dashboard_path("dashboard/appointments/<int:pk>/delete/", views.AppointmentDeleteView.as_view(), name="appointment-record-delete"),

    dashboard_path("dashboard/testimonials/", views.TestimonialListView.as_view(), name="testimonial-list"),
    dashboard_path("dashboard/testimonials/create/", views.TestimonialCreateView.as_view(), name="testimonial-create"),
    dashboard_path("dashboard/testimonials/<int:pk>/edit/", views.TestimonialUpdateView.as_view(), name="testimonial-update"),
    dashboard_path("dashboard/testimonials/<int:pk>/delete/", views.TestimonialDeleteView.as_view(), name="testimonial-delete"),

    dashboard_path("dashboard/events/", views.EventRecordListView.as_view(), name="event-record-list"),
    dashboard_path("dashboard/events/create/", views.EventRecordCreateView.as_view(), name="event-record-create"),
    dashboard_path("dashboard/events/<int:pk>/edit/", views.EventRecordUpdateView.as_view(), name="event-record-update"),
    dashboard_path("dashboard/events/<int:pk>/delete/", views.EventRecordDeleteView.as_view(), name="event-record-delete"),

    dashboard_path("dashboard/estates/", views.EstateListView.as_view(), name="estate-list"),
    dashboard_path("dashboard/estates/create/", views.EstateCreateView.as_view(), name="estate-create"),
    dashboard_path("dashboard/estates/<int:pk>/edit/", views.EstateUpdateView.as_view(), name="estate-update"),
    dashboard_path("dashboard/estates/<int:pk>/delete/", views.EstateDeleteView.as_view(), name="estate-delete"),

    dashboard_path("dashboard/vehicles/", views.VehicleListView.as_view(), name="vehicle-list"),
    dashboard_path("dashboard/vehicles/create/", views.VehicleCreateView.as_view(), name="vehicle-create"),
    dashboard_path("dashboard/vehicles/<int:pk>/edit/", views.VehicleUpdateView.as_view(), name="vehicle-update"),
    dashboard_path("dashboard/vehicles/<int:pk>/delete/", views.VehicleDeleteView.as_view(), name="vehicle-delete"),
]