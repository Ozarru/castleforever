from django import forms

from .models import Booking, ContactInquiry, ServiceRequest, VehicleRental


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