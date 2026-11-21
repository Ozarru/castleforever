from django.conf import settings
from django.shortcuts import render

from catalog.models import Estate
from core.marketing import marketing_snapshot
from core.models import Testimonial
from core.seo import graph_schema, item_list_schema, page_seo, web_page_schema


def _seo(title, description, *, page_type="website", schema=None, path="/"):
    return page_seo(
        title,
        description,
        page_type=page_type,
        schema=graph_schema(web_page_schema(title, description, f"{settings.SITE_URL}{path}"), schema),
    )


def home(request):
    estates = Estate.objects.filter(is_published=True).order_by("country", "name")[:6]
    title = "CastleForever | Castle Wedding Estates in France, Italy, Spain & Portugal"
    description = (
        "Discover exceptional castle, palace and villa wedding estates across France, "
        "Italy, Spain, Germany and Portugal. Explore venues, plan your celebration and "
        "enquire with CastleForever."
    )
    return render(request, "base/home.html", {
        "estates": estates,
        "testimonials": Testimonial.objects.filter(is_published=True).select_related("estate")[:3],
        "results": marketing_snapshot(),
        "seo": _seo(title, description),
    })


def privacy(request):
    title = "Privacy Policy | CastleForever"
    description = "How CastleForever handles the information you share when planning your celebration."
    return render(request, "legal/privacy.html", {"seo": _seo(title, description, path="/privacy/")})


def terms(request):
    title = "Terms & Conditions | CastleForever"
    description = "Terms and conditions for using the CastleForever wedding estate planning service."
    return render(request, "legal/terms.html", {"seo": _seo(title, description, path="/terms/")})


def cookies(request):
    title = "Cookie Policy | CastleForever"
    description = "Learn which cookies CastleForever uses and how they support your experience."
    return render(request, "legal/cookies.html", {"seo": _seo(title, description, path="/cookies/")})


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
    sections = _estate_type_sections()
    title = "Wedding Destinations & Estate Types | CastleForever"
    description = (
        "Browse castle, palace, villa, manor and garden wedding estates by destination "
        "in France, Italy, Spain, Germany and Portugal."
    )
    schema = item_list_schema(
        title,
        f"{settings.SITE_URL}/destinations/",
        [(section["label"], f"/estates/?estate_type={section['key']}") for section in sections],
    )
    return render(request, "base/destinations.html", {
        "estate_types": sections,
        "seo": _seo(title, description, page_type="CollectionPage", schema=schema, path="/destinations/"),
    })


def approach(request):
    title = "Our Planning & Payment Approach | CastleForever"
    description = (
        "See how CastleForever helps you plan a destination wedding, from choosing an "
        "estate to a clear, staged payment approach."
    )
    return render(request, "base/approach.html", {
        "seo": _seo(title, description, path="/approach/"),
    })


# Backwards/alternative-friendly aliases
our_approach = approach
our_approach_page = approach
