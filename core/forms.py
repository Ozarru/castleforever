from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Appointment, Booking, ContactInquiry, ServiceRequest, VehicleRental


class BookingEnquiryForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("full_name", "email", "wedding_date", "guest_count", "message")
        widgets = {"wedding_date": forms.DateInput(attrs={"type": "date"}), "message": forms.Textarea(attrs={"rows": 4})}


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        widgets = {"wedding_date": forms.DateInput(attrs={"type": "date"}), "message": forms.Textarea(attrs={"rows": 4})}


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ("full_name", "email", "phone", "destination", "event_type", "event_date", "guest_count", "budget", "needs")
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "needs": forms.Textarea(attrs={"rows": 5}),
        }


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ("full_name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class VehicleRentalForm(forms.ModelForm):
    class Meta:
        model = VehicleRental
        fields = "__all__"
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            "full_name",
            "email",
            "phone",
            "appointment_type",
            "preferred_date",
            "preferred_time",
            "estate",
            "guest_count",
            "message",
        )
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_date"].widget.attrs.setdefault("min", date.today().isoformat())
        estate_filter = Q(is_published=True)
        if self.instance.pk and self.instance.estate_id:
            estate_filter |= Q(pk=self.instance.estate_id)
        self.fields["estate"].queryset = self.fields["estate"].queryset.filter(estate_filter)

    def clean_preferred_date(self):
        preferred = self.cleaned_data.get("preferred_date")
        if preferred and not self.instance.pk and preferred < date.today():
            raise ValidationError(_("Please choose a date in the future."))
        return preferred