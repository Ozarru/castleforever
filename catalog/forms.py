from django import forms

from .models import Vehicle, Estate


class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = "__all__"


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"