from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class Booking(models.Model):
    class Status(models.TextChoices):
        ENQUIRY = "enquiry", "Enquiry"
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    venue = models.ForeignKey("catalog.Venue", on_delete=models.PROTECT, related_name="bookings")
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    wedding_date = models.DateField()
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ENQUIRY)
    quoted_venue_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venue} — {self.full_name} ({self.wedding_date})"


class VehicleRental(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="vehicle_rentals")
    vehicle = models.ForeignKey("catalog.Vehicle", on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    is_paid = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})


class PaymentSchedule(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment_schedule")
    deposit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("3000.00"))
    installment_months = models.PositiveSmallIntegerField(default=36)
    # Schedule is a proposal, not a loan agreement or automatic charge.
    approved = models.BooleanField(default=False)

    @property
    def monthly_estimate(self):
        if self.booking.quoted_venue_total is None or not self.installment_months:
            return None
        return max(Decimal("0.00"), self.booking.quoted_venue_total - self.deposit) / self.installment_months


class ServiceRequest(models.Model):
    DESTINATION_CHOICES = [
        ("FR", _("France")),
        ("IT", _("Italy")),
        ("ES", _("Spain")),
        # ("other", _("Other")),
    ]
    EVENT_CHOICES = [
        ("wedding", _("Wedding")),
        ("engagement", _("Engagement")),
        ("anniversary", _("Anniversary")),
        ("corporate", _("Corporate event")),
        # ("other", _("Other")),
    ]
    full_name = models.CharField(_("Full name"), max_length=180)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=40, blank=True)
    destination = models.CharField(_("Destination"), max_length=10, choices=DESTINATION_CHOICES, blank=True)
    event_type = models.CharField(_("Event type"), max_length=20, choices=EVENT_CHOICES, default="wedding")
    event_date = models.DateField(_("Event date"), null=True, blank=True)
    guest_count = models.PositiveIntegerField(_("Guest count"), null=True, blank=True)
    budget = models.CharField(_("Budget"), max_length=80, blank=True)
    needs = models.TextField(_("Your needs"), help_text=_("Describe your needs and expectations"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.get_event_type_display()}"


class ContactInquiry(models.Model):
    full_name = models.CharField(_("Full name"), max_length=180)
    email = models.EmailField(_("Email"))
    subject = models.CharField(_("Subject"), max_length=180, blank=True)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.subject or _('Inquiry')}"
