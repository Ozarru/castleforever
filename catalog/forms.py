from django import forms

from .models import Vehicle, Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = "__all__"


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"