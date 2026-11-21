from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Appointment, Booking, ContactInquiry, NotificationRead, ServiceRequest


def _read_keys(user):
    if not user or not user.is_authenticated:
        return set()
    return set(NotificationRead.objects.filter(user=user).values_list("key", flat=True))


def get_dashboard_notifications(user, limit=5, include_read=False):
    """Return recent actionable requests for the dashboard bell dropdown.

    Each item has a stable ``key`` so read state can be stored per user without
    adding flags to the source models.
    """
    if not user or not user.is_authenticated or not user.is_staff:
        return []

    read_keys = set() if include_read else _read_keys(user)
    items = []

    for booking in Booking.objects.filter(status=Booking.Status.ENQUIRY):
        items.append(
            {
                "key": f"booking:{booking.pk}",
                "title": _("New booking enquiry: %(name)s") % {"name": booking.full_name},
                "meta": str(booking.estate),
                "url": reverse("core:booking-update", args=[booking.pk]),
                "icon": "fa-calendar-check",
                "created_at": booking.created_at,
            }
        )

    for service_request in ServiceRequest.objects.all():
        items.append(
            {
                "key": f"service-request:{service_request.pk}",
                "title": _("New service request: %(name)s") % {"name": service_request.full_name},
                "meta": service_request.get_event_type_display(),
                "url": reverse("core:service-request-update", args=[service_request.pk]),
                "icon": "fa-clipboard-list",
                "created_at": service_request.created_at,
            }
        )

    for inquiry in ContactInquiry.objects.all():
        items.append(
            {
                "key": f"contact-inquiry:{inquiry.pk}",
                "title": _("New contact inquiry: %(name)s") % {"name": inquiry.full_name},
                "meta": inquiry.subject,
                "url": reverse("core:contact-inquiry-update", args=[inquiry.pk]),
                "icon": "fa-envelope",
                "created_at": inquiry.created_at,
            }
        )

    for appointment in Appointment.objects.filter(status=Appointment.Status.REQUESTED):
        items.append(
            {
                "key": f"appointment:{appointment.pk}",
                "title": _("Appointment requested: %(name)s") % {"name": appointment.full_name},
                "meta": appointment.get_appointment_type_display(),
                "url": reverse("core:appointment-record-update", args=[appointment.pk]),
                "icon": "fa-calendar-day",
                "created_at": appointment.created_at,
            }
        )

    items.sort(key=lambda item: item["created_at"], reverse=True)
    if not include_read:
        items = [item for item in items if item["key"] not in read_keys]
    if limit is not None:
        items = items[:limit]
    return items


def mark_notifications_read(user):
    """Mark every currently visible dashboard notification as read."""
    if not user or not user.is_authenticated or not user.is_staff:
        return 0

    keys = [
        item["key"]
        for item in get_dashboard_notifications(user, limit=None, include_read=True)
    ]
    created = NotificationRead.objects.bulk_create(
        [NotificationRead(user=user, key=key) for key in keys],
        ignore_conflicts=True,
    )
    return len(created)
