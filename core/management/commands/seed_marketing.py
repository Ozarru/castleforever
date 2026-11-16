"""Seed demo reviews and 2025 wedding results used by the public marketing pages."""

from datetime import date

from django.core.management.base import BaseCommand

from catalog.models import Venue
from core.models import Testimonial, WeddingRecord

TESTIMONIALS = [
    {
        "couple_names": "Camille & Antoine",
        "venue_slug": "chateau-de-lumiere",
        "location": "Loire Valley, France",
        "event_date": date(2025, 6, 14),
        "rating": 5,
        "quote": (
            "We visited five châteaux before choosing this one, and the difference was immediate. "
            "The team knew every detail of the house, the garden and the light at sunset. "
            "Our guests still talk about the dinner on the terrace."
        ),
        "image_url": "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Sofia & Marco",
        "venue_slug": "villa-toscana-serenita",
        "location": "Tuscany, Italy",
        "event_date": date(2025, 9, 6),
        "rating": 5,
        "quote": (
            "The payment schedule made the difference for us. We confirmed the villa eighteen months "
            "ahead and spread the balance without compromising on the celebration. The coordinator "
            "handled our suppliers as if they were her own."
        ),
        "image_url": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Elena & Rafael",
        "venue_slug": "palacio-de-sevilla",
        "location": "Andalusia, Spain",
        "event_date": date(2025, 5, 24),
        "rating": 5,
        "quote": (
            "We wanted a warm, family celebration with a real sense of place. The palace courtyard, "
            "the orange trees and the flamenco at midnight were perfect. Every question we sent was "
            "answered within a day."
        ),
        "image_url": "https://images.unsplash.com/photo-1522673607200-164d1b6ce486?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Charlotte & James",
        "venue_slug": "domaine-de-la-seine",
        "location": "Normandy, France",
        "event_date": date(2025, 7, 19),
        "rating": 5,
        "quote": (
            "An intimate wedding for 92 guests by the river. The team was discreet, precise and "
            "genuinely kind. The timeline they gave us was followed to the minute, which meant we "
            "could actually enjoy the day."
        ),
        "image_url": "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Aurélie & Thomas",
        "venue_slug": "manoir-de-bourgogne",
        "location": "Burgundy, France",
        "event_date": date(2025, 8, 30),
        "rating": 4,
        "quote": (
            "A beautiful manor and a very professional team. We would have liked one more meeting "
            "with the caterer earlier in the process, but the wedding itself was flawless and the "
            "cellar dinner was unforgettable."
        ),
        "image_url": "https://images.unsplash.com/photo-1529636798458-92182e662485?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Marta & Luca",
        "venue_slug": "palazzo-del-lago",
        "location": "Lake Como, Italy",
        "event_date": date(2025, 6, 28),
        "rating": 5,
        "quote": (
            "Arriving by boat with our families was the moment we will remember forever. The lakeside "
            "terrace, the mountain light and the team's calm made the whole weekend feel effortless."
        ),
        "image_url": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Inès & Pablo",
        "venue_slug": "castillo-de-mallorca",
        "location": "Mallorca, Spain",
        "event_date": date(2025, 9, 20),
        "rating": 5,
        "quote": (
            "We planned from Madrid and only visited twice. The guided video tour, the written "
            "proposal and the coordinator's patience made a destination wedding feel simple. "
            "The sunset ceremony was exactly as we had imagined."
        ),
        "image_url": "https://images.unsplash.com/photo-1591604466107-ec97de577aff?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Léa & Nicolas",
        "venue_slug": "chateau-de-provence",
        "location": "Provence, France",
        "event_date": date(2025, 5, 10),
        "rating": 5,
        "quote": (
            "The lavender was in bloom, the courtyard was full of our friends, and the team had "
            "thought of everything  -  from the shade for older guests to the last taxi home. "
            "We felt looked after from the first call."
        ),
        "image_url": "https://images.unsplash.com/photo-1606216794074-735e91aa2c92?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "couple_names": "Giulia & Matteo",
        "venue_slug": "castello-umbro",
        "location": "Umbria, Italy",
        "event_date": date(2025, 10, 4),
        "rating": 5,
        "quote": (
            "A restored castle in the middle of the olive groves, with a dinner in the courtyard "
            "and a party that lasted until sunrise. The planning checklist kept us organised "
            "without ever feeling like a constraint."
        ),
        "image_url": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?auto=format&fit=crop&w=1200&q=80",
    },
]

# A realistic 2025 season: busiest between May and September.
WEDDINGS_PER_MONTH = {
    1: 2,
    2: 3,
    3: 5,
    4: 7,
    5: 11,
    6: 16,
    7: 14,
    8: 9,
    9: 12,
    10: 6,
    11: 3,
    12: 2,
}

FIRST_NAMES = [
    "Camille", "Antoine", "Sofia", "Marco", "Elena", "Rafael", "Charlotte", "James",
    "Aurélie", "Thomas", "Marta", "Luca", "Inès", "Pablo", "Léa", "Nicolas",
    "Giulia", "Matteo", "Emma", "Hugo", "Clara", "Louis", "Alba", "Diego",
    "Freya", "Oliver", "Nora", "Elias", "Maya", "Gabriel",
]

SECOND_NAMES = [
    "Martin", "Bernard", "Dubois", "Robert", "Petit", "Durand", "Leroy", "Moreau",
    "Simon", "Laurent", "Roux", "Fournier", "Girard", "André", "Mercier", "Blanc",
]


class Command(BaseCommand):
    help = "Populate demo reviews and 2025 wedding records for the marketing pages."

    def handle(self, *args, **options):
        venues = {venue.slug: venue for venue in Venue.objects.all()}
        fallback_venues = list(venues.values())
        fallback_countries = ["FR", "IT", "ES"]

        testimonial_count = 0
        for index, data in enumerate(TESTIMONIALS):
            testimonial, created = Testimonial.objects.update_or_create(
                couple_names=data["couple_names"],
                defaults={
                    "venue": venues.get(data["venue_slug"]),
                    "location": data["location"],
                    "event_date": data["event_date"],
                    "rating": data["rating"],
                    "quote": data["quote"],
                    "image_url": data["image_url"],
                    "is_published": True,
                    "position": index,
                },
            )
            testimonial_count += 1
            self.stdout.write(
                f"{'Created' if created else 'Updated'} testimonial: {testimonial.couple_names}"
            )

        counter = 0
        wedding_count = 0
        for month, month_total in WEDDINGS_PER_MONTH.items():
            for slot in range(month_total):
                counter += 1
                reference = f"CF-2025-{counter:03d}"
                day = min(3 + slot * 2, 27)
                venue = fallback_venues[counter % len(fallback_venues)] if fallback_venues else None
                country = venue.country if venue else fallback_countries[counter % 3]
                first = FIRST_NAMES[counter % len(FIRST_NAMES)]
                second = FIRST_NAMES[(counter * 7 + 3) % len(FIRST_NAMES)]
                if second == first:
                    second = FIRST_NAMES[(counter + 1) % len(FIRST_NAMES)]

                _, created = WeddingRecord.objects.update_or_create(
                    reference=reference,
                    defaults={
                        "venue": venue,
                        "country": country,
                        "wedding_date": date(2025, month, day),
                        "couple_names": f"{first} & {second} {SECOND_NAMES[counter % len(SECOND_NAMES)]}",
                        "guest_count": 80 + (counter * 13) % 121,
                        "notes": "Seeded demo record.",
                    },
                )
                wedding_count += 1
                if created:
                    self.stdout.write(f"Created wedding record: {reference}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {testimonial_count} testimonials and {wedding_count} wedding records populated."
            )
        )
