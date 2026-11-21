import csv
import html
import io
import json
import re

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from catalog.models import Estate
from core.data_transfer import DATASETS, XLSX_CONTENT_TYPE
from core.marketing import marketing_snapshot, results_snapshot
from core.models import Booking, ContactInquiry, NotificationRead, ServiceRequest, WeddingRecord


class DashboardImportExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="staff", email="staff@example.com", password="pass", is_staff=True
        )
        cls.estate = Estate.objects.create(
            name="Test Estate",
            slug="test-estate",
            country="FR",
            region="Provence",
            city="Amboise",
            description="A test estate",
            capacity=100,
            price_from="5000.00",
            is_published=True,
        )

    def setUp(self):
        self.client.force_login(self.staff)

    def _booking(self, name="Alice Example"):
        return Booking.objects.create(
            estate=self.estate,
            full_name=name,
            email="alice@example.com",
            wedding_date="2027-06-15",
            guest_count=80,
            status=Booking.Status.CONFIRMED,
            quoted_estate_total="9000.00",
        )

    def test_public_estate_pages_render(self):
        self.assertEqual(self.client.get(reverse("catalog:estates")).status_code, 200)
        self.assertEqual(self.client.get(self.estate.get_absolute_url()).status_code, 200)

    def test_statistics_page_has_structured_chart_payload(self):
        self._booking()
        response = self.client.get(reverse("core:statistics"))
        self.assertEqual(response.status_code, 200)

        match = re.search(
            r'<script id="statistics-charts" type="application/json">(.*?)</script>',
            response.content.decode(),
            re.S,
        )
        self.assertIsNotNone(match)
        payload = json.loads(html.unescape(match.group(1)))

        self.assertEqual(payload["summary"][0]["label"], "Bookings")
        self.assertEqual(payload["summary"][0]["value"], 1)
        self.assertTrue(payload["chart_sections"])
        self.assertEqual(payload["chart_sections"][0]["id"], "bookings-inquiries")
        self.assertTrue(payload["chart_sections"][0]["icon"])
        bookings_chart = payload["chart_sections"][0]["charts"][0]
        self.assertEqual(bookings_chart["id"], "bookings-by-estate")
        self.assertEqual(bookings_chart["labels"], ["Test Estate"])
        self.assertEqual(bookings_chart["data"], [1])

    def test_statistics_page_has_section_tabs(self):
        response = self.client.get(reverse("core:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'id="tab-bookings-inquiries"')
        self.assertContains(response, 'id="panel-bookings-inquiries"')
        self.assertContains(response, 'data-tab-target="panel-service-requests"')
        self.assertContains(response, 'aria-selected="true"', count=1)

    def test_dashboard_sidebar_has_icons_logo_and_collapse_control(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="dashboardTitleBar"')
        self.assertContains(response, 'id="sidebarToggle"')
        self.assertContains(response, "styles.css?v=")
        self.assertContains(response, 'sidebar-logo-icon')
        self.assertContains(response, 'brand/icon')
        self.assertContains(response, 'brand/logo-alt')
        self.assertContains(response, "sidebar-link flex items-center gap-3")
        self.assertContains(response, "fa-solid fa-chart-simple")
        self.assertContains(response, "sidebar-collapsed")

    def test_dashboard_titlebar_has_display_tools_and_user_menu(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-theme-toggle")
        self.assertContains(response, "data-lang-toggle")
        self.assertContains(response, 'id="dashboardLanguageMenu"')
        self.assertContains(response, reverse("set_language"))
        self.assertContains(response, "Português")
        self.assertContains(response, 'data-popover-menu="dashboardUserMenu"')
        self.assertContains(response, 'id="dashboardUserMenu"')
        self.assertContains(response, reverse("accounts:profile"))
        self.assertContains(response, reverse("accounts:logout"))

    def test_notification_bell_opens_dropdown_with_clickable_notification(self):
        booking = Booking.objects.create(
            estate=self.estate,
            full_name="Notify Me",
            email="notify@example.com",
            wedding_date="2027-08-12",
            guest_count=40,
            status=Booking.Status.ENQUIRY,
        )
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-popover-menu="dashboardNotificationsMenu"')
        self.assertContains(response, 'id="dashboardNotificationsMenu"')
        self.assertContains(response, 'class="notification-badge"')
        self.assertContains(response, reverse("core:booking-update", args=[booking.pk]))
        self.assertContains(response, "Notify Me")
        self.assertContains(response, reverse("core:notifications-mark-read"))
        self.assertContains(response, "Mark all as read")

        mark_url = reverse("core:notifications-mark-read")
        response = self.client.post(mark_url, {"next": reverse("core:dashboard")})
        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertEqual(NotificationRead.objects.filter(user=self.staff).count(), 1)

        after = self.client.get(reverse("core:dashboard"))
        self.assertEqual(after.context["notification_count"], 0)
        self.assertNotContains(after, "Notify Me")

    def test_generic_detail_page_and_table_link(self):
        booking = self._booking()
        detail_url = reverse("core:dashboard-detail", args=["core.booking", booking.pk])
        list_response = self.client.get(reverse("core:booking-list"))
        self.assertContains(list_response, detail_url)
        self.assertContains(list_response, "fa-arrow-right-long")
        self.assertContains(list_response, 'id="rowActionsMenu_1"')
        self.assertContains(list_response, 'data-popover-menu="rowActionsMenu_1"')
        self.assertContains(list_response, reverse("core:booking-update", args=[booking.pk]))
        self.assertContains(list_response, reverse("core:booking-delete", args=[booking.pk]))

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Example")
        self.assertContains(response, "Wedding date")
        self.assertContains(response, reverse("core:booking-update", args=[booking.pk]))

        missing = reverse("core:dashboard-detail", args=["core.unknown", booking.pk])
        self.assertEqual(self.client.get(missing).status_code, 404)

    def test_list_tables_show_relevant_dataset_columns(self):
        self._booking()

        estates = self.client.get(reverse("core:estate-list"))
        for label in ["Country", "Estate type", "Region", "City", "Capacity", "Price from", "Published"]:
            self.assertContains(estates, label)
        for value in ["France", "Castle", "Provence", "Amboise", "100", "5000.00"]:
            self.assertContains(estates, value)

        bookings = self.client.get(reverse("core:booking-list"))
        for label in ["Wedding date", "Guest count", "Status", "Quoted total"]:
            self.assertContains(bookings, label)
        for value in ["2027-06-15", "80", "Confirmed", "9000.00"]:
            self.assertContains(bookings, value)

    def test_list_view_has_import_and_export_buttons(self):
        response = self.client.get(reverse("core:booking-list"))
        self.assertContains(response, reverse("core:dashboard-import", args=["core.booking"]))
        self.assertContains(response, reverse("core:dashboard-export", args=["core.booking"]))
        self.assertContains(response, 'class="dashboard-outline-button"', count=2)
        self.assertContains(response, 'name="format"')
        self.assertContains(response, "CSV")
        self.assertContains(response, "XLSX")
        self.assertContains(response, "Import")
        self.assertContains(response, "Export")

    def test_import_page_offers_both_file_formats(self):
        response = self.client.get(reverse("core:dashboard-import", args=["core.booking"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="format"')
        self.assertContains(response, 'name="data_file"')
        self.assertContains(response, "File format")
        self.assertContains(response, "Data file")
        self.assertContains(response, "XLSX")

    def test_export_then_import_restores_records(self):
        original = self._booking()
        export_url = reverse("core:dashboard-export", args=["core.booking"])
        response = self.client.get(export_url)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(rows[0][0], "id")
        self.assertIn("full_name", rows[0])
        self.assertEqual(len(rows), 2)

        original_pk = original.pk
        Booking.objects.all().delete()
        self.assertEqual(Booking.objects.count(), 0)

        upload = SimpleUploadedFile(
            "bookings.csv", response.content, content_type="text/csv"
        )
        import_url = reverse("core:dashboard-import", args=["core.booking"])
        response = self.client.post(import_url, {"csv_file": upload}, follow=True)
        self.assertEqual(response.status_code, 200)
        restored = Booking.objects.get(pk=original_pk)
        self.assertEqual(restored.full_name, "Alice Example")
        self.assertEqual(restored.estate, self.estate)
        self.assertEqual(restored.status, Booking.Status.CONFIRMED)

    def test_xlsx_export_then_import_restores_records(self):
        original = self._booking()
        export_url = reverse("core:dashboard-export", args=["core.booking"])
        response = self.client.get(export_url, {"format": "xlsx"})
        self.assertEqual(response["Content-Type"], XLSX_CONTENT_TYPE)

        workbook = load_workbook(io.BytesIO(response.content), read_only=True, data_only=True)
        rows = list(workbook.active.iter_rows(values_only=True))
        self.assertEqual(rows[0][0], "id")
        self.assertIn("full_name", rows[0])
        workbook.close()

        original_pk = original.pk
        Booking.objects.all().delete()

        upload = SimpleUploadedFile(
            "bookings.xlsx", response.content, content_type=XLSX_CONTENT_TYPE
        )
        import_url = reverse("core:dashboard-import", args=["core.booking"])
        response = self.client.post(
            import_url,
            {"data_file": upload, "format": "xlsx"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        restored = Booking.objects.get(pk=original_pk)
        self.assertEqual(restored.full_name, "Alice Example")
        self.assertEqual(restored.estate, self.estate)
        self.assertEqual(restored.status, Booking.Status.CONFIRMED)

    def test_new_row_without_id_is_created(self):
        csv_text = (
            "id,user,estate,full_name,email,wedding_date,guest_count,message,"
            "status,quoted_estate_total\r\n"
            f",,{self.estate.pk},Bob Example,bob@example.com,2027-08-20,50,,enquiry,7000.00\r\n"
        )
        upload = SimpleUploadedFile("new.csv", csv_text.encode(), content_type="text/csv")
        response = self.client.post(
            reverse("core:dashboard-import", args=["core.booking"]),
            {"csv_file": upload},
        )
        self.assertEqual(response.status_code, 302)
        created = Booking.objects.get(full_name="Bob Example")
        self.assertEqual(created.guest_count, 50)

    def test_invalid_file_rolls_back_everything(self):
        csv_text = (
            "id,user,estate,full_name,email,wedding_date,guest_count,message,"
            "status,quoted_estate_total\r\n"
            f",,{self.estate.pk},Good Row,good@example.com,2027-08-20,50,,enquiry,7000.00\r\n"
            f",,{self.estate.pk},,bad@example.com,2027-08-20,50,,enquiry,7000.00\r\n"
        )
        upload = SimpleUploadedFile("bad.csv", csv_text.encode(), content_type="text/csv")
        response = self.client.post(
            reverse("core:dashboard-import", args=["core.booking"]),
            {"csv_file": upload},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "was not completed")
        self.assertEqual(Booking.objects.count(), 0)

    def test_every_dashboard_dataset_exposes_both_export_formats(self):
        for model_key in DATASETS:
            with self.subTest(model_key=model_key, file_format="csv"):
                response = self.client.get(
                    reverse("core:dashboard-export", args=[model_key])
                )
                self.assertEqual(response.status_code, 200)
                first_line = response.content.decode().splitlines()[0]
                self.assertTrue(first_line.startswith("id,"))

            with self.subTest(model_key=model_key, file_format="xlsx"):
                response = self.client.get(
                    reverse("core:dashboard-export", args=[model_key]),
                    {"format": "xlsx"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], XLSX_CONTENT_TYPE)
                workbook = load_workbook(
                    io.BytesIO(response.content), read_only=True, data_only=True
                )
                self.assertEqual(workbook.active["A1"].value, "id")
                workbook.close()

    def test_unknown_dataset_is_404(self):
        response = self.client.get(reverse("core:dashboard-export", args=["core.user"]))
        self.assertEqual(response.status_code, 404)

    def test_non_staff_cannot_export(self):
        other = get_user_model().objects.create_user(
            username="other", email="other@example.com", password="pass"
        )
        self.client.force_login(other)
        response = self.client.get(reverse("core:dashboard-export", args=["core.booking"]))
        self.assertEqual(response.status_code, 403)


class PublicHomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for index in range(1, 8):
            Estate.objects.create(
                name=f"Estate {index:02d}",
                slug=f"estate-{index:02d}",
                country="FR",
                region="Provence",
                description=f"Description {index}",
                capacity=100,
                price_from="5000.00",
                is_published=True,
            )

    def test_home_limits_collection_to_six_estates(self):
        response = self.client.get(reverse("base:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["estates"]), 6)
        self.assertContains(response, "Estate 01")
        self.assertContains(response, "Estate 06")
        self.assertNotContains(response, "Estate 07")

    def test_home_collection_has_view_all_link_and_no_country_filter(self):
        response = self.client.get(reverse("base:home"))

        self.assertContains(response, "View all estates")
        self.assertContains(response, f'href="{reverse("catalog:estates")}"')
        self.assertNotContains(response, 'data-filter')
        self.assertNotContains(response, 'data-estate-country')
        self.assertNotContains(response, 'data-country-link')
        self.assertNotContains(response, 'id="filters"')

    def test_navbar_has_no_results_or_reviews_links(self):
        response = self.client.get(reverse("base:home"))
        results_url = reverse("core:results")
        reviews_url = reverse("core:reviews")

        self.assertNotContains(
            response,
            f'<a href="{results_url}" class="hover:text-[#dccba7]">Results</a>',
        )
        self.assertNotContains(
            response,
            f'<a href="{reviews_url}" class="hover:text-[#dccba7]">Reviews</a>',
        )
        self.assertNotContains(
            response,
            f'<a class="block" href="{results_url}">2025 results</a>',
        )
        self.assertNotContains(
            response,
            f'<a class="block" href="{reviews_url}">Reviews</a>',
        )


class MarketingSnapshotTests(TestCase):
    def test_empty_wedding_records_use_complete_default_snapshot(self):
        snapshot = results_snapshot()

        self.assertEqual(snapshot["total"], 52)
        self.assertEqual(snapshot["guests"], 12519)
        self.assertEqual(snapshot["average_guests"], 241)
        self.assertEqual(snapshot["estate_count"], 24)
        self.assertEqual(
            [month["count"] for month in snapshot["months"]],
            [1, 2, 3, 4, 5, 6, 8, 9, 7, 4, 2, 1],
        )
        self.assertEqual(snapshot["peak_month"]["label"], "Aug")
        self.assertEqual(snapshot["peak_month"]["count"], 9)
        self.assertEqual(
            [(row["code"], row["total"]) for row in snapshot["by_country"]],
            [("FR", 24), ("IT", 13), ("ES", 9), ("PT", 4), ("DE", 2)],
        )
        self.assertEqual(
            [(row["estate__name"], row["total"]) for row in snapshot["by_estate"]],
            [
                ("Chateau de Lumiere", 6),
                ("Villa Toscana Serenita", 5),
                ("Chateau de Provence", 5),
                ("Palacio de Sevilla", 4),
                ("Palazzo del Lago", 4),
                ("Castello Umbro", 3),
            ],
        )
        self.assertEqual(
            sum(month["count"] for month in snapshot["months"]),
            snapshot["total"],
        )
        self.assertEqual(sum(row["total"] for row in snapshot["by_country"]), snapshot["total"])

        home_snapshot = marketing_snapshot()
        self.assertEqual(home_snapshot["rating_average"], 4.5)
        self.assertEqual(home_snapshot["testimonial_count"], 0)

    def test_public_pages_render_with_empty_marketing_tables(self):
        for url_name in ["base:home", "core:results", "core:reviews"]:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_results_page_renders_default_breakdowns(self):
        response = self.client.get(reverse("core:results"))

        self.assertContains(response, "Chateau de Lumiere")
        self.assertContains(response, "Villa Toscana Serenita")
        self.assertContains(response, "Aug")
        self.assertNotContains(
            response,
            "Country results will appear once the first 2025 records are published.",
        )

    def test_results_snapshot_uses_real_records_when_available(self):
        estate = Estate.objects.create(
            name="Marketing Estate",
            slug="marketing-estate",
            country="FR",
            region="Provence",
            description="A test estate",
            capacity=100,
            price_from="5000.00",
            is_published=True,
        )
        WeddingRecord.objects.create(
            reference="WR-2025-001",
            estate=estate,
            country="FR",
            wedding_date="2025-06-15",
            guest_count=100,
        )
        WeddingRecord.objects.create(
            reference="WR-2025-002",
            estate=estate,
            country="FR",
            wedding_date="2025-08-20",
            guest_count=80,
        )

        snapshot = results_snapshot()

        self.assertEqual(snapshot["total"], 2)
        self.assertEqual(snapshot["guests"], 180)
        self.assertEqual(snapshot["average_guests"], 90)
        self.assertEqual(snapshot["estate_count"], 1)
        self.assertEqual(snapshot["by_country"][0]["code"], "FR")
        self.assertEqual(snapshot["by_country"][0]["total"], 2)
        self.assertEqual(snapshot["by_estate"][0]["estate__name"], "Marketing Estate")
        self.assertEqual(snapshot["by_estate"][0]["total"], 2)
        self.assertEqual(
            [month["count"] for month in snapshot["months"]],
            [1 if month in (6, 8) else 0 for month in range(1, 13)],
        )


class ContactPageTests(TestCase):
    def test_contact_page_has_tabs_forms_and_information_panel(self):
        response = self.client.get(reverse("core:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "enquiry")
        for needle in [
            'role="tablist"',
            'id="tabEnquiryBtn"',
            'id="tabRequestBtn"',
            'aria-labelledby="tabEnquiryBtn"',
            'aria-labelledby="tabRequestBtn" hidden',
            'name="form_type" value="enquiry"',
            'name="form_type" value="request"',
            "hello@castleforever.com",
            "What happens next",
            "privacy policy",
        ]:
            self.assertContains(response, needle)
        self.assertRegex(response.content.decode(), r'id="tabEnquiryBtn"[^>]*aria-selected="true"')
        self.assertRegex(response.content.decode(), r'id="tabRequestBtn"[^>]*aria-selected="false"')

    def test_tab_query_selects_service_request_panel(self):
        response = self.client.get(reverse("core:contact"), {"tab": "request"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "request")
        self.assertRegex(response.content.decode(), r'id="tabRequestBtn"[^>]*aria-selected="true"')
        self.assertContains(response, 'aria-labelledby="tabEnquiryBtn" hidden')
        self.assertNotContains(response, 'aria-labelledby="tabRequestBtn" hidden')

    def test_needs_redirects_to_request_tab(self):
        response = self.client.get(reverse("core:needs"))

        self.assertRedirects(response, "/contact/?tab=request")

    def test_enquiry_submission_saves_and_shows_confirmation(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "form_type": "enquiry",
                "enquiry-full_name": "Alice Example",
                "enquiry-email": "alice@example.com",
                "enquiry-subject": "A question",
                "enquiry-message": "Do you have dates in June?",
            },
            follow=True,
        )

        self.assertEqual(response.redirect_chain, [("/contact/?tab=enquiry", 302)])
        self.assertEqual(ContactInquiry.objects.count(), 1)
        self.assertContains(response, "Thank you. Your message has been received.")
        self.assertContains(response, "fa-circle-check")

    def test_service_request_submission_saves_and_shows_confirmation(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "form_type": "request",
                "request-full_name": "Bob Example",
                "request-email": "bob@example.com",
                "request-phone": "+33 1 00 00 00 00",
                "request-destination": "FR",
                "request-event_type": "wedding",
                "request-event_date": "2027-06-15",
                "request-guest_count": "120",
                "request-budget": "30000",
                "request-needs": "We are looking for a castle in the Loire Valley.",
            },
            follow=True,
        )

        self.assertEqual(response.redirect_chain, [("/contact/?tab=request", 302)])
        self.assertEqual(ServiceRequest.objects.count(), 1)
        self.assertContains(response, "Thank you. We have received your request.")

    def test_invalid_enquiry_shows_errors_and_keeps_enquiry_tab(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "form_type": "enquiry",
                "enquiry-full_name": "Alice Example",
                "enquiry-email": "",
                "enquiry-subject": "",
                "enquiry-message": "Hello",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "enquiry")
        self.assertContains(response, "This field is required.")
        self.assertEqual(ContactInquiry.objects.count(), 0)


class PaymentApproachPageTests(TestCase):
    def test_approach_page_uses_light_layout_without_image_hero(self):
        response = self.client.get(reverse("base:approach"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="hero')
        self.assertNotContains(response, 'section class="bg-forest text-white')
        self.assertContains(response, 'bg-[#F0EDE5] border-b')
        self.assertEqual(content.count("Your dream day. Your own pace."), 1)

    def test_approach_page_has_one_consistent_payment_calculator(self):
        response = self.client.get(reverse("base:approach"))
        content = response.content.decode()

        for field_id in ["deposit", "price", "years", "monthly"]:
            self.assertEqual(content.count(f'id="{field_id}"'), 1)
        self.assertContains(response, "price - deposit")
        self.assertContains(response, "€3,000")
        self.assertNotContains(response, "price / months")

