from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Estate

class Booking(models.Model):
    class Status(models.TextChoices):
        ENQUIRY = "enquiry", "Enquiry"
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    estate = models.ForeignKey("catalog.Estate", on_delete=models.PROTECT, related_name="bookings")
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    wedding_date = models.DateField()
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ENQUIRY)
    quoted_estate_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estate}  -  {self.full_name} ({self.wedding_date})"


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
        if self.booking.quoted_estate_total is None or not self.installment_months:
            return None
        return max(Decimal("0.00"), self.booking.quoted_estate_total - self.deposit) / self.installment_months


class ServiceRequest(models.Model):
    DESTINATION_CHOICES = [
        ("FR", _("France")),
        ("IT", _("Italy")),
        ("ES", _("Spain")),
        ("DE", _("Germany")),
        ("PT", _("Portugal")),
        # ("other", _("Other")),
    ]
    EVENT_CHOICES = [
        ("wedding", _("Wedding")),
        ("engagement", _("Engagement")),
        ("anniversary", _("Anniversary")),
        ("corporate", _("Corporate event")),
        ("other", _("Other")),
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
        return f"{self.full_name}  -  {self.get_event_type_display()}"


class ContactInquiry(models.Model):
    full_name = models.CharField(_("Full name"), max_length=180)
    email = models.EmailField(_("Email"))
    subject = models.CharField(_("Subject"), max_length=180, blank=True)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}  -  {self.subject or _('Inquiry')}"


class Testimonial(models.Model):
    """A published couple review, shown on the reviews and home pages."""

    couple_names = models.CharField(_("Couple names"), max_length=180)
    estate = models.ForeignKey(
        "catalog.Estate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
        verbose_name=_("Estate"),
    )
    location = models.CharField(_("Location"), max_length=120, blank=True)
    event_date = models.DateField(_("Event date"), null=True, blank=True)
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    quote = models.TextField(_("Testimonial"))
    image = models.ImageField(_("Photo"), upload_to="testimonials/", blank=True)
    image_url = models.URLField(_("Photo URL"), blank=True)
    is_published = models.BooleanField(_("Published"), default=True)
    position = models.PositiveSmallIntegerField(_("Display order"), default=0)

    class Meta:
        ordering = ["position", "-event_date", "pk"]
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def stars(self):
        return range(self.rating)

    @property
    def empty_stars(self):
        return range(5 - self.rating)

    def __str__(self):
        return f"{self.couple_names}  -  {self.rating}/5"


EVENT_TYPE_CHOICES = [
    ("wedding", _("Wedding")),
    ("engagement", _("Engagement")),
    ("anniversary", _("Anniversary")),
    ("corporate", _("Corporate event")),
    ("other", _("Other")),
]


class EventRecord(models.Model):
    """A completed event, used to publish verified yearly results."""

    reference = models.CharField(_("Reference"), max_length=40, unique=True, null=True, blank=True)
    estate = models.ForeignKey(
        "catalog.Estate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_records",
        verbose_name=_("Estate"),
    )
    country = models.CharField(_("Country"), max_length=2, choices=Estate.COUNTRY_CHOICES, blank=True)
    event_type = models.CharField(
        _("Event type"),
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default="wedding",
    )
    event_date = models.DateField(_("Event date"))
    client_names = models.CharField(_("Client names"), max_length=180, blank=True)
    guest_count = models.PositiveIntegerField(_("Guest count"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date"]
        verbose_name = _("Event record")
        verbose_name_plural = _("Event records")

    def __str__(self):
        label = self.client_names or _("Event")
        return f"{label}  -  {self.event_date}"


class Appointment(models.Model):
    """A consultation request submitted from the public appointment page."""

    class Kind(models.TextChoices):
        VIDEO = "video", _("Video call")
        PHONE = "phone", _("Phone call")
        VISIT = "visit", _("Estate visit")

    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    full_name = models.CharField(_("Full name"), max_length=180)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=40, blank=True)
    appointment_type = models.CharField(
        _("Appointment type"),
        max_length=10,
        choices=Kind.choices,
        default=Kind.VIDEO,
    )
    preferred_date = models.DateField(_("Preferred date"))
    preferred_time = models.TimeField(_("Preferred time"))
    estate = models.ForeignKey(
        "catalog.Estate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        verbose_name=_("Estate of interest"),
    )
    guest_count = models.PositiveIntegerField(_("Estimated guest count"), null=True, blank=True)
    message = models.TextField(_("What would you like to discuss?"), blank=True)
    status = models.CharField(
        _("Status"),
        max_length=12,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")

    def __str__(self):
        return (
            f"{self.full_name}  -  {self.get_appointment_type_display()}  -  "
            f"{self.preferred_date} {self.preferred_time:%H:%M}"
        )


class NotificationRead(models.Model):
    """Tracks dashboard notifications a staff user has marked as read."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_notification_reads",
    )
    key = models.CharField(max_length=100)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-read_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "key"],
                name="uniq_dashboard_notification_read",
            )
        ]
        verbose_name = _("Notification read")
        verbose_name_plural = _("Notification reads")

    def __str__(self):
        return f"{self.user} - {self.key}"
