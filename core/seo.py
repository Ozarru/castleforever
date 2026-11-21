"""Shared helpers for public-page SEO metadata and structured data."""
import json
import re

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import get_language

OG_LOCALES = {
    "en": "en_US",
    "fr": "fr_FR",
    "it": "it_IT",
    "es": "es_ES",
    "de": "de_DE",
    "pt": "pt_PT",
}

# Several legacy URLs render the same page. Canonicalise them to one preferred
# path instead of letting search engines split ranking signals across aliases.
CANONICAL_PATHS = {
    "/destination/": "/destinations/",
    "/our-approach/": "/approach/",
    "/our_approach/": "/approach/",
    "/payment-approach/": "/approach/",
    "/payments/": "/approach/",
    "/rentals/": "/cars/",
    "/vehicles/": "/cars/",
    "/needs/": "/contact/",
    "/inquiry/": "/contact/",
    "/enquire/": "/contact/",
    "/testimonials/": "/reviews/",
    "/2025-results/": "/results/",
    "/book-a-call/": "/appointment/",
}


def absolute_url(path):
    """Turn a static/media path into an absolute URL on the canonical origin."""
    if not path:
        return ""
    value = str(path)
    if value.startswith(("http://", "https://", "//")):
        return value
    return f"{settings.SITE_URL.rstrip('/')}/{value.lstrip('/')}"


def clean_description(value, limit=160):
    """Flatten translated/HTML descriptions into a safe meta description."""
    text = strip_tags(str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return Truncator(text).chars(limit)


def json_for_schema(schema):
    """Serialize JSON-LD safely for embedding inside a <script> tag."""
    if not schema:
        return ""
    return json.dumps(
        schema,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).replace("</", "<\\/")


def canonical_path(path):
    return CANONICAL_PATHS.get(path, path)


def canonical_url(request):
    """Canonical public URL, without tracking or filter query strings."""
    return f"{settings.SITE_URL.rstrip('/')}{canonical_path(request.path)}"


def robots_content():
    if getattr(settings, "NOINDEX", False) or settings.DEBUG:
        return "noindex, nofollow"
    return "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"


def og_locale():
    code = (get_language() or "en").split("-")[0]
    return OG_LOCALES.get(code, "en_US")


def page_seo(title, description, *, image=None, page_type="website", schema=None, noindex=False):
    """Build the per-view SEO context consumed by the public layout."""
    return {
        "title": str(title),
        "description": clean_description(description),
        "image": absolute_url(image or static("images/og-default.jpg")),
        "type": page_type,
        "schema_json": json_for_schema(schema),
        "noindex": noindex,
    }


def graph_schema(*schemas):
    items = [schema for schema in schemas if schema]
    if not items:
        return None
    return {"@context": "https://schema.org", "@graph": items}


def web_page_schema(name, description, url):
    return {
        "@type": "WebPage",
        "name": name,
        "description": clean_description(description, 300),
        "url": url,
        "inLanguage": (get_language() or "en").split("-")[0],
    }


def breadcrumb_schema(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": absolute_url(path),
            }
            for position, (name, path) in enumerate(items, start=1)
        ],
    }


def estate_schema(estate):
    """Product + Offer + breadcrumb schema for an estate detail page."""
    url = absolute_url(estate.get_absolute_url())
    image = absolute_url(estate.cover_url) if estate.cover_url else ""
    location = ", ".join(
        part for part in (estate.city, estate.region, estate.get_country_display()) if part
    )
    product = {
        "@type": "Product",
        "name": str(estate.name),
        "description": clean_description(estate.localized_description, 300),
        "url": url,
        "category": str(estate.get_estate_type_display()),
        "offers": {
            "@type": "Offer",
            "price": str(estate.price_from),
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock",
            "url": url,
        },
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Capacity", "value": estate.capacity},
            {"@type": "PropertyValue", "name": "Location", "value": location},
        ],
    }
    if image:
        product["image"] = [image]

    breadcrumbs = breadcrumb_schema([
        ("Home", "/"),
        ("Estates", "/estates/"),
        (str(estate.name), estate.get_absolute_url()),
    ])
    return graph_schema(web_page_schema(str(estate.name), estate.localized_description, url), product, breadcrumbs)


def item_list_schema(name, url, items):
    """Schema for a collection page, e.g. estates or destinations."""
    return {
        "@type": "CollectionPage",
        "name": name,
        "url": url,
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "url": absolute_url(item_url),
                    "name": str(item_name),
                }
                for position, (item_name, item_url) in enumerate(items, start=1)
            ],
        },
    }
