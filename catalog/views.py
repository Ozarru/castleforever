from django.shortcuts import get_object_or_404, render

from core.forms import BookingEnquiryForm
from .models import Vehicle, Venue

def venues(request):
    venues = Venue.objects.filter(is_published=True).order_by("country", "name")
    return render(request, "catalog/venues.html", {"venues": venues})

def venue_detail(request, slug):
    venue = get_object_or_404(Venue.objects.prefetch_related("images"), slug=slug, is_published=True)
    similar = Venue.objects.filter(is_published=True, country=venue.country).exclude(pk=venue.pk).order_by("name")[:3]
    return render(request, "catalog/venue_detail.html", {"venue": venue, "similar_venues": similar, "booking_form": BookingEnquiryForm()})

def car_rentals(request):
    vehicles = Vehicle.objects.filter(is_available=True).order_by("category", "name")
    return render(request, "catalog/car_rentals.html", {"vehicles": vehicles})
