from django.contrib import admin
from .models import Booking, ContactInquiry, PaymentSchedule, ServiceRequest, VehicleRental

class VehicleRentalInline(admin.TabularInline):
    model = VehicleRental
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("venue", "full_name", "wedding_date", "guest_count", "status", "created_at")
    list_filter = ("status", "wedding_date")
    search_fields = ("full_name", "email", "venue__name")
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
