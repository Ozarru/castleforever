"""Marketing helpers shared by the public home, reviews and results pages."""

from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractMonth

from catalog.models import Venue

from .models import Testimonial, WeddingRecord

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


def monthly_wedding_counts(year=RESULTS_YEAR):
    """Return the number of recorded weddings for each month of ``year``."""
    rows = (
        WeddingRecord.objects.filter(wedding_date__year=year)
        .annotate(month=ExtractMonth("wedding_date"))
        .values("month")
        .annotate(total=Count("id"))
    )
    totals = {row["month"]: row["total"] for row in rows}
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


def results_snapshot(year=RESULTS_YEAR):
    """Aggregate the public 2025 results shown as social proof."""
    records = WeddingRecord.objects.filter(wedding_date__year=year)
    total = records.count()
    guests = records.aggregate(total=Sum("guest_count"))["total"] or 0
    months = monthly_wedding_counts(year)
    peak_month = max(months, key=lambda month: month["count"], default=None)

    country_labels = dict(Venue.COUNTRY_CHOICES)
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
    by_venue = list(
        records.exclude(venue__isnull=True)
        .values("venue__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:6]
    )

    return {
        "year": year,
        "total": total,
        "guests": guests,
        "average_guests": round(guests / total) if total else 0,
        "months": months,
        "peak_month": peak_month if peak_month and peak_month["count"] else None,
        "by_country": by_country,
        "by_venue": by_venue,
        "estate_count": records.exclude(venue__isnull=True).values("venue").distinct().count(),
    }


def testimonial_rating():
    """Average published rating, or ``None`` when there are no reviews yet."""
    return Testimonial.objects.filter(is_published=True).aggregate(average=Avg("rating"))["average"]


def marketing_snapshot(year=RESULTS_YEAR):
    """Compact numbers for the homepage social-proof band."""
    snapshot = results_snapshot(year)
    snapshot["rating_average"] = testimonial_rating()
    snapshot["testimonial_count"] = Testimonial.objects.filter(is_published=True).count()
    return snapshot
