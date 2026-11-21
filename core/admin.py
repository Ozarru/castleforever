from django.contrib import admin
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

class VehicleRentalInline(admin.TabularInline):
    model = VehicleRental
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("estate", "full_name", "wedding_date", "guest_count", "status", "created_at")
    list_filter = ("status", "wedding_date")
    search_fields = ("full_name", "email", "estate__name")
    inlines = [VehicleRentalInline]

@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ("booking", "deposit", "installment_months", "approved")


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "event_type", "event_date", "guest_count", "created_at")
    search_fields = ("full_name", "email", "needs")


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject", "created_at")
    search_fields = ("full_name", "email", "subject", "message")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("couple_names", "estate", "event_date", "rating", "is_published", "position")
    list_filter = ("is_published", "rating", "estate__country")
    search_fields = ("couple_names", "quote", "estate__name")
    list_editable = ("is_published", "position")


@admin.register(WeddingRecord)
class WeddingRecordAdmin(admin.ModelAdmin):
    list_display = ("reference", "couple_names", "estate", "wedding_date", "guest_count", "country")
    list_filter = ("country", "wedding_date")
    search_fields = ("reference", "couple_names", "estate__name")
    date_hierarchy = "wedding_date"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "appointment_type",
        "preferred_date",
        "preferred_time",
        "estate",
        "status",
        "created_at",
    )
    list_filter = ("status", "appointment_type", "preferred_date")
    search_fields = ("full_name", "email", "phone", "message")
    date_hierarchy = "preferred_date"
