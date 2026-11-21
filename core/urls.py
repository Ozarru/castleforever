from django.urls import path
from . import views

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
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/statistics/", views.StatisticsView.as_view(), name="statistics"),
    path("dashboard/detail/<str:model_key>/<int:pk>/", views.DashboardDetailView.as_view(), name="dashboard-detail"),
    path("dashboard/notifications/read/", views.DashboardNotificationsMarkReadView.as_view(), name="notifications-mark-read"),

    path("dashboard/data/<str:model_key>/bulk/", views.DashboardBulkActionView.as_view(), name="dashboard-bulk"),
    path("dashboard/data/<str:model_key>/export/", views.DashboardExportView.as_view(), name="dashboard-export"),
    path("dashboard/data/<str:model_key>/import/", views.DashboardImportView.as_view(), name="dashboard-import"),

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

    path("dashboard/appointments/", views.AppointmentListView.as_view(), name="appointment-record-list"),
    path("dashboard/appointments/create/", views.AppointmentCreateView.as_view(), name="appointment-record-create"),
    path("dashboard/appointments/<int:pk>/edit/", views.AppointmentUpdateView.as_view(), name="appointment-record-update"),
    path("dashboard/appointments/<int:pk>/delete/", views.AppointmentDeleteView.as_view(), name="appointment-record-delete"),

    path("dashboard/testimonials/", views.TestimonialListView.as_view(), name="testimonial-list"),
    path("dashboard/testimonials/create/", views.TestimonialCreateView.as_view(), name="testimonial-create"),
    path("dashboard/testimonials/<int:pk>/edit/", views.TestimonialUpdateView.as_view(), name="testimonial-update"),
    path("dashboard/testimonials/<int:pk>/delete/", views.TestimonialDeleteView.as_view(), name="testimonial-delete"),

    path("dashboard/wedding-records/", views.WeddingRecordListView.as_view(), name="wedding-record-list"),
    path("dashboard/wedding-records/create/", views.WeddingRecordCreateView.as_view(), name="wedding-record-create"),
    path("dashboard/wedding-records/<int:pk>/edit/", views.WeddingRecordUpdateView.as_view(), name="wedding-record-update"),
    path("dashboard/wedding-records/<int:pk>/delete/", views.WeddingRecordDeleteView.as_view(), name="wedding-record-delete"),

    path("dashboard/estates/", views.EstateListView.as_view(), name="estate-list"),
    path("dashboard/estates/create/", views.EstateCreateView.as_view(), name="estate-create"),
    path("dashboard/estates/<int:pk>/edit/", views.EstateUpdateView.as_view(), name="estate-update"),
    path("dashboard/estates/<int:pk>/delete/", views.EstateDeleteView.as_view(), name="estate-delete"),

    path("dashboard/vehicles/", views.VehicleListView.as_view(), name="vehicle-list"),
    path("dashboard/vehicles/create/", views.VehicleCreateView.as_view(), name="vehicle-create"),
    path("dashboard/vehicles/<int:pk>/edit/", views.VehicleUpdateView.as_view(), name="vehicle-update"),
    path("dashboard/vehicles/<int:pk>/delete/", views.VehicleDeleteView.as_view(), name="vehicle-delete"),
]