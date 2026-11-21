from django.shortcuts import render
from catalog.models import Estate
from core.marketing import marketing_snapshot
from core.models import Testimonial

def home(request):
    estates = Estate.objects.filter(is_published=True).order_by("country", "name")[:6]
    return render(request, "base/home.html", {
        "estates": estates,
        "testimonials": Testimonial.objects.filter(is_published=True).select_related("estate")[:3],
        "results": marketing_snapshot(),
    })

def privacy(request):
    return render(request, "legal/privacy.html")

def terms(request):
    return render(request, "legal/terms.html")

def cookies(request):
    return render(request, "legal/cookies.html")

def _estate_type_sections():
    """Group published estates into sections ordered by the model's type choices."""
    grouped = {}
    estates = Estate.objects.filter(is_published=True).order_by("estate_type", "country", "name")
    for estate in estates:
        grouped.setdefault(estate.estate_type, []).append(estate)

    sections = []
    for value, label in Estate.EstateType.choices:
        if value in grouped:
            sections.append({
                "key": value,
                "label": label,
                "estates": grouped[value][:3],
            })
    return sections


def destinations(request):
    return render(request, "base/destinations.html", {
        "estate_types": _estate_type_sections(),
    })

def approach(request):
    return render(request, "base/approach.html")

# Backwards/alternative-friendly aliases
our_approach = approach
our_approach_page = approach
