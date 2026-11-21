from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import Estate, EstateImage


class EstateModelTests(TestCase):
    def setUp(self):
        self.estate = Estate.objects.create(
            name="Test Estate",
            slug="test-estate",
            country="FR",
            region="Provence",
            description="English description",
            description_fr="Description française",
            capacity=100,
            price_from="5000.00",
            is_published=True,
        )

    def test_choices_have_valid_labels(self):
        self.assertIn(("PT", "Portugal"), Estate.COUNTRY_CHOICES)
        self.assertIn(("castle", "Castle"), Estate.ESTATE_TYPE_CHOICES)
        self.assertEqual(dict(Estate.COUNTRY_CHOICES)["FR"], "France")

    def test_estate_type_defaults_to_castle(self):
        self.assertEqual(self.estate.estate_type, "castle")

    def test_localized_description_uses_current_language_with_fallback(self):
        with translation.override("fr"):
            self.assertEqual(self.estate.localized_description, "Description française")
        with translation.override("de"):
            self.assertEqual(self.estate.localized_description, "English description")


class PublicCatalogPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        common = {
            "description": "A beautiful venue for a celebration.",
            "capacity": 120,
            "price_from": "15000.00",
            "is_published": True,
        }
        cls.castle = Estate.objects.create(
            name="Amboise Castle",
            slug="amboise-castle",
            country="FR",
            region="Loire Valley",
            city="Amboise",
            estate_type="castle",
            cover_image_url="https://example.com/castle-cover.jpg",
            **common,
        )
        EstateImage.objects.create(
            estate=cls.castle,
            image_url="https://example.com/castle-courtyard.jpg",
            alt_text="Castle courtyard",
            position=0,
        )
        cls.palace = Estate.objects.create(
            name="Como Palace",
            slug="como-palace",
            country="IT",
            region="Lake Como",
            city="Como",
            estate_type="palace",
            **common,
        )
        cls.villa = Estate.objects.create(
            name="Florence Villa",
            slug="florence-villa",
            country="IT",
            region="Tuscany",
            city="Florence",
            estate_type="villa",
            **common,
        )
        cls.hidden = Estate.objects.create(
            name="Hidden Manor",
            slug="hidden-manor",
            country="ES",
            region="Andalusia",
            city="Seville",
            estate_type="manor",
            description="Not published yet.",
            capacity=80,
            price_from="9000.00",
            is_published=False,
        )

    @staticmethod
    def _names(response):
        return [estate.name for estate in response.context["estates"]]

    def test_destinations_are_grouped_by_estate_type(self):
        response = self.client.get(reverse("base:destinations"))

        self.assertEqual(response.status_code, 200)
        sections = response.context["estate_types"]
        self.assertEqual([section["key"] for section in sections], ["castle", "palace", "villa"])
        self.assertEqual([section["label"] for section in sections], ["Castle", "Palace", "Villa"])
        self.assertEqual(sections[0]["estates"], [self.castle])
        self.assertContains(response, 'id="type-castle"')
        self.assertContains(response, 'id="type-palace"')
        self.assertContains(response, 'id="type-villa"')
        self.assertNotContains(response, 'id="france"')
        self.assertNotContains(response, "Hidden Manor")

    def test_destination_cards_and_view_all_link_to_filtered_estates(self):
        response = self.client.get(reverse("base:destinations"))
        estates_url = reverse("catalog:estates")

        for key in ["castle", "palace", "villa"]:
            self.assertContains(response, f'href="{estates_url}?estate_type={key}"')
        self.assertEqual(
            response.content.decode().count(f'href="{estates_url}?estate_type=castle"'),
            2,
        )
        self.assertContains(response, f'href="{estates_url}"')

    def test_each_estate_type_section_shows_at_most_three_estates(self):
        for index in range(1, 5):
            Estate.objects.create(
                name=f"Extra Castle {index:02d}",
                slug=f"extra-castle-{index:02d}",
                country="FR",
                region="Burgundy",
                city="Dijon",
                estate_type="castle",
                description="Another castle.",
                capacity=90,
                price_from="12000.00",
                is_published=True,
            )

        response = self.client.get(reverse("base:destinations"))
        castle_section = next(
            section for section in response.context["estate_types"] if section["key"] == "castle"
        )

        self.assertEqual(len(castle_section["estates"]), 3)
        self.assertContains(response, "Extra Castle 01")
        self.assertContains(response, "Extra Castle 02")
        self.assertNotContains(response, "Extra Castle 03")
        self.assertNotContains(response, "Extra Castle 04")

    def test_estate_detail_has_gallery_sticky_summary_and_enquiry_anchor(self):
        response = self.client.get(self.castle.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["gallery"]), 2)
        self.assertEqual(response.context["gallery"][0]["url"], "https://example.com/castle-cover.jpg")
        self.assertEqual(response.context["gallery"][1]["alt"], "Castle courtyard")
        for needle in [
            'id="estateCarousel"',
            'id="carouselCounter"',
            'id="carouselThumbs"',
            'id="enquire"',
            'lg:sticky',
            'id="mobileEnquiryBar"',
            'aria-label="Previous image"',
        ]:
            self.assertContains(response, needle)

    def test_similar_estates_are_filled_when_type_has_few_entries(self):
        response = self.client.get(self.castle.get_absolute_url())

        self.assertEqual(
            [estate.name for estate in response.context["similar_estates"]],
            ["Como Palace", "Florence Villa"],
        )
        self.assertNotIn(self.castle, response.context["similar_estates"])
        self.assertNotIn(self.hidden, response.context["similar_estates"])

    def test_estates_page_has_search_block(self):
        response = self.client.get(reverse("catalog:estates"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._names(response), ["Amboise Castle", "Como Palace", "Florence Villa"])
        for field in ['name="q"', 'name="estate_type"', 'name="country"', 'name="region"']:
            self.assertContains(response, field)
        self.assertContains(response, "All estate types")
        self.assertContains(response, "All countries")
        self.assertContains(response, "All regions")

    def test_estates_search_matches_name_city_and_country_label(self):
        url = reverse("catalog:estates")

        self.assertEqual(self._names(self.client.get(url, {"q": "Amboise"})), ["Amboise Castle"])
        self.assertEqual(self._names(self.client.get(url, {"q": "Como"})), ["Como Palace"])
        self.assertEqual(self._names(self.client.get(url, {"q": "France"})), ["Amboise Castle"])
        self.assertEqual(self._names(self.client.get(url, {"q": "Tuscany"})), ["Florence Villa"])

    def test_estates_filters_combine_with_search(self):
        url = reverse("catalog:estates")

        self.assertEqual(
            self._names(self.client.get(url, {"estate_type": "palace"})),
            ["Como Palace"],
        )
        self.assertEqual(
            self._names(self.client.get(url, {"country": "IT"})),
            ["Como Palace", "Florence Villa"],
        )
        self.assertEqual(
            self._names(self.client.get(url, {"region": "Tuscany"})),
            ["Florence Villa"],
        )
        self.assertEqual(
            self._names(self.client.get(url, {
                "q": "Como",
                "estate_type": "palace",
                "country": "IT",
            })),
            ["Como Palace"],
        )

    def test_invalid_filter_values_are_ignored_and_unpublished_stay_hidden(self):
        url = reverse("catalog:estates")
        response = self.client.get(url, {"estate_type": "not-a-type", "country": "XX"})

        self.assertEqual(len(self._names(response)), 3)
        self.assertNotContains(response, "Hidden Manor")
        self.assertContains(response, "3 estates found")
