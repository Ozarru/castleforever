import re
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static

from .notifications import get_dashboard_notifications
from .seo import absolute_url, canonical_url, json_for_schema, og_locale, robots_content


def static_versions(request):
    """Expose a changing version for the unhashed custom stylesheet.

    Development serves ``styles.css`` without a content hash, so browsers can
    keep an old copy after a CSS edit. Appending the source file's mtime forces
    a fresh download whenever the stylesheet changes.
    """
    styles_path = Path(settings.BASE_DIR) / "static" / "styles.css"
    try:
        version = int(styles_path.stat().st_mtime)
    except OSError:
        version = 0
    return {"STYLES_VERSION": version}


def dashboard_notifications(request):
    """Expose recent actionable requests and their count to templates."""
    items = get_dashboard_notifications(getattr(request, "user", None))
    return {
        "dashboard_notifications": items,
        "notification_count": len(items),
    }


def seo(request):
    """Public-site SEO defaults, canonical URL and optional tracking config."""
    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL,
    }
    if settings.SITE_EMAIL:
        organization["email"] = settings.SITE_EMAIL
    if settings.SITE_PHONE:
        organization["telephone"] = settings.SITE_PHONE

    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL,
    }

    return {
        "SITE_URL": settings.SITE_URL,
        "SITE_NAME": settings.SITE_NAME,
        "SITE_EMAIL": settings.SITE_EMAIL,
        "SITE_PHONE": settings.SITE_PHONE,
        "SITE_PHONE_TEL": re.sub(r"[^\d+]", "", settings.SITE_PHONE),
        "canonical_url": canonical_url(request),
        "robots_content": robots_content(),
        "og_locale": og_locale(),
        "default_og_image": absolute_url(static("images/og-default.jpg")),
        "organization_schema_json": json_for_schema(organization),
        "website_schema_json": json_for_schema(website),
        "GOOGLE_SITE_VERIFICATION": settings.GOOGLE_SITE_VERIFICATION,
        "GOOGLE_ANALYTICS_ID": settings.GOOGLE_ANALYTICS_ID,
        "GOOGLE_TAG_MANAGER_ID": settings.GOOGLE_TAG_MANAGER_ID,
        "GOOGLE_ADS_ID": settings.GOOGLE_ADS_ID,
        "GOOGLE_ADS_CONVERSION_LABEL": settings.GOOGLE_ADS_CONVERSION_LABEL,
        "primary_tracking_id": settings.GOOGLE_ANALYTICS_ID or settings.GOOGLE_ADS_ID,
    }
