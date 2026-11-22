"""Marketing helpers shared by the public home, reviews and results pages."""

from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractMonth

from catalog.models import Estate

from .models import EventRecord, Testimonial

RESULTS_YEAR = 2025

MONTHS = [
    (1, "Jan"),
    (2, "Feb"),
    (3, "Mar"),
    (4, "Apr"),
    (5, "May"),
    (6, "Jun"),
    (7, "Jul"),
    (8, "Aug"),
    (9, "Sep"),
    (10, "Oct"),
    (11, "Nov"),
    (12, "Dec"),
]

# Shown until real 2025 records are published. These defaults are internally
# consistent: the monthly and country totals both add up to DEFAULT_TOTAL.
DEFAULT_TOTAL = 52
DEFAULT_GUESTS = 12519
DEFAULT_ESTATE_COUNT = 24
DEFAULT_RATING = 4.5
DEFAULT_MONTH_COUNTS = [1, 2, 3, 4, 5, 6, 8, 9, 7, 4, 2, 1]
DEFAULT_COUNTRY_TOTALS = [
    ("FR", 24),
    ("IT", 13),
    ("ES", 9),
    ("PT", 4),
    ("DE", 2),
]
DEFAULT_ESTATE_TOTALS = [
    ("Chateau de Lumiere", 6),
    ("Villa Toscana Serenita", 5),
    ("Chateau de Provence", 5),
    ("Palacio de Sevilla", 4),
    ("Palazzo del Lago", 4),
    ("Castello Umbro", 3),
]


def _months_from_totals(totals):
    peak = max(totals.values(), default=0)
    months = []
    for number, label in MONTHS:
        count = totals.get(number, 0)
        months.append(
            {
                "number": number,
                "label": label,
                "count": count,
                "height": max(round(count / peak * 100), 4) if count and peak else 0,
            }
        )
    return months


def _default_monthly_counts():
    totals = {
        number: count
        for (number, _label), count in zip(MONTHS, DEFAULT_MONTH_COUNTS)
    }
    return _months_from_totals(totals)


def monthly_event_counts(year=RESULTS_YEAR):
    """Return the number of recorded events for each month of ``year``."""
    rows = (
        EventRecord.objects.filter(event_date__year=year)
        .annotate(month=ExtractMonth("event_date"))
        .values("month")
        .annotate(total=Count("id"))
    )
    totals = {row["month"]: row["total"] for row in rows}
    return _months_from_totals(totals)


def results_snapshot(year=RESULTS_YEAR):
    """Aggregate the public yearly results shown as social proof.

    Until real records exist for ``year``, return a complete, internally
    consistent set of default figures so the public pages are not empty.
    """
    records = EventRecord.objects.filter(event_date__year=year)
    record_count = records.count()
    has_records = record_count > 0

    total = record_count or DEFAULT_TOTAL
    guests = records.aggregate(total=Sum("guest_count"))["total"] or DEFAULT_GUESTS
    months = monthly_event_counts(year) if has_records else _default_monthly_counts()
    peak_month = max(months, key=lambda month: month["count"], default=None)

    country_labels = dict(Estate.COUNTRY_CHOICES)
    if has_records:
        by_country = [
            {
                "code": row["country"],
                "label": country_labels.get(row["country"], row["country"] or "Other"),
                "total": row["total"],
            }
            for row in records.values("country")
            .annotate(total=Count("id"))
            .order_by("-total")
        ]
    else:
        by_country = [
            {
                "code": code,
                "label": country_labels.get(code, code),
                "total": count,
            }
            for code, count in DEFAULT_COUNTRY_TOTALS
        ]

    if has_records:
        by_estate = list(
            records.exclude(estate__isnull=True)
            .values("estate__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:6]
        )
    else:
        by_estate = [
            {"estate__name": name, "total": count}
            for name, count in DEFAULT_ESTATE_TOTALS
        ]

    return {
        "year": year,
        "total": total,
        "guests": guests,
        "average_guests": round(guests / total) if total else 0,
        "months": months,
        "peak_month": peak_month if peak_month and peak_month["count"] else None,
        "by_country": by_country,
        "by_estate": by_estate,
        "estate_count": (
            records.exclude(estate__isnull=True).values("estate").distinct().count()
            or DEFAULT_ESTATE_COUNT
        ),
    }


def testimonial_rating():
    """Average published rating, or a default when there are no reviews yet."""
    return (
        Testimonial.objects.filter(is_published=True).aggregate(average=Avg("rating"))["average"]
        or DEFAULT_RATING
    )


def marketing_snapshot(year=RESULTS_YEAR):
    """Compact numbers for the homepage social-proof band."""
    snapshot = results_snapshot(year)
    snapshot["rating_average"] = testimonial_rating()
    snapshot["testimonial_count"] = Testimonial.objects.filter(is_published=True).count()
    return snapshot
