from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from core.forms import BookingEnquiryForm
from core.seo import estate_schema, graph_schema, item_list_schema, page_seo, web_page_schema
from .models import Vehicle, Estate


def _valid_choice(choices, value):
    """Return a submitted choice only when it is one of the model's options."""
    value = (value or "").strip()
    return value if value in dict(choices) else ""


def estates(request):
    query = (request.GET.get("q") or "").strip()
    estate_type = _valid_choice(Estate.EstateType.choices, request.GET.get("estate_type"))
    country = _valid_choice(Estate.Country.choices, request.GET.get("country"))
    region = (request.GET.get("region") or "").strip()

    published = Estate.objects.filter(is_published=True)
    matching = published

    if query:
        search = (
            Q(name__icontains=query)
            | Q(city__icontains=query)
            | Q(region__icontains=query)
            | Q(country__icontains=query)
        )
        # Country is stored as a two-letter code, so also match its translated
        # label (for example "France" should find records stored as "FR").
        for code, label in Estate.Country.choices:
            if query.lower() in str(label).lower():
                search |= Q(country=code)
        matching = matching.filter(search)

    if estate_type:
        matching = matching.filter(estate_type=estate_type)
    if country:
        matching = matching.filter(country=country)
    if region:
        matching = matching.filter(region__iexact=region)

    matching = matching.order_by("estate_type", "country", "name")
    regions = published.values_list("region", flat=True).distinct().order_by("region")

    title = "Castle, Palace & Villa Wedding Estates | CastleForever"
    description = (
        "Browse published wedding estates across Europe. Filter by castle, palace, "
        "villa, manor or garden, country and region to find your setting."
    )
    schema = graph_schema(
        web_page_schema(title, description, f"{settings.SITE_URL}/estates/"),
        item_list_schema(
            title,
            f"{settings.SITE_URL}/estates/",
            [(estate.name, estate.get_absolute_url()) for estate in matching[:20]],
        ),
    )

    return render(request, "catalog/estates.html", {
        "estates": matching,
        "query": query,
        "estate_types": Estate.EstateType.choices,
        "countries": Estate.Country.choices,
        "regions": regions,
        "selected_estate_type": estate_type,
        "selected_country": country,
        "selected_region": region,
        "has_filters": bool(query or estate_type or country or region),
        "seo": page_seo(title, description, page_type="CollectionPage", schema=schema),
    })


def estate_detail(request, slug):
    estate = get_object_or_404(Estate.objects.prefetch_related("images"), slug=slug, is_published=True)

    gallery = []
    if estate.cover_url:
        gallery.append({"url": estate.cover_url, "alt": estate.name})
    for photo in estate.images.all():
        if photo.url:
            gallery.append({"url": photo.url, "alt": photo.alt_text or estate.name})

    # Prefer the same estate type, then fill any remaining slots so the page
    # always has useful suggestions even when a type has few entries.
    similar = list(
        Estate.objects.filter(is_published=True, estate_type=estate.estate_type)
        .exclude(pk=estate.pk)
        .order_by("country", "name")[:3]
    )
    if len(similar) < 3:
        excluded = [estate.pk] + [item.pk for item in similar]
        similar.extend(
            Estate.objects.filter(is_published=True)
            .exclude(pk__in=excluded)
            .order_by("country", "name")[:3 - len(similar)]
        )

    type_label = estate.get_estate_type_display()
    country_label = estate.get_country_display()
    title = f"{estate.name} | {type_label} Wedding Estate in {country_label} | CastleForever"
    description = (
        f"{estate.name} is a {type_label} wedding estate in "
        f"{', '.join(part for part in (estate.city, estate.region, country_label) if part)}, "
        f"hosting up to {estate.capacity} guests."
    )

    return render(request, "catalog/estate_detail.html", {
        "estate": estate,
        "gallery": gallery,
        "similar_estates": similar,
        "booking_form": BookingEnquiryForm(),
        "seo": page_seo(
            title,
            description,
            image=estate.cover_url,
            page_type="product",
            schema=estate_schema(estate),
        ),
    })


def car_rentals(request):
    vehicles = Vehicle.objects.filter(is_available=True).order_by("category", "name")
    title = "Wedding Guest Transport & Car Rentals | CastleForever"
    description = (
        "Explore chauffeur and guest transport options for destination weddings "
        "in France, Italy, Spain, Germany and Portugal."
    )
    return render(request, "catalog/car_rentals.html", {
        "vehicles": vehicles,
        "seo": page_seo(
            title,
            description,
            schema=graph_schema(web_page_schema(title, description, f"{settings.SITE_URL}/cars/")),
        ),
    })
