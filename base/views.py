from django.shortcuts import render
from catalog.models import Venue

def home(request):
    venues = Venue.objects.filter(is_published=True).order_by("country", "name")
    return render(request, "base/home.html", {"venues": venues})

def privacy(request):
    return render(request, "legal/privacy.html")

def terms(request):
    return render(request, "legal/terms.html")

def cookies(request):
    return render(request, "legal/cookies.html")

def destinations(request):
    venues = Venue.objects.filter(is_published=True).order_by("country", "name")
    return render(request, "base/destinations.html", {"venues": venues})

def approach(request):
    venues = Venue.objects.filter(is_published=True).order_by("country", "name")
    return render(request, "base/approach.html", {"venues": venues})

# Backwards/alternative-friendly aliases
our_approach = approach
our_approach_page = approach
