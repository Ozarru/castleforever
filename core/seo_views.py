"""robots.txt and sitemap.xml endpoints for the public site."""
from xml.etree import ElementTree as ET

from django.conf import settings
from django.http import HttpResponse

from catalog.models import Estate

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

STATIC_PAGES = [
    ("/", "1.0", "daily"),
    ("/destinations/", "0.9", "weekly"),
    ("/estates/", "0.9", "weekly"),
    ("/approach/", "0.7", "monthly"),
    ("/reviews/", "0.7", "monthly"),
    ("/results/", "0.6", "monthly"),
    ("/contact/", "0.8", "monthly"),
    ("/cars/", "0.6", "monthly"),
    ("/privacy/", "0.3", "yearly"),
    ("/terms/", "0.3", "yearly"),
    ("/cookies/", "0.3", "yearly"),
]


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /i18n/",
        "Disallow: /healthz/",
    ]
    if settings.NOINDEX or settings.DEBUG:
        lines.insert(1, "Disallow: /")
    else:
        lines.extend(["", f"Sitemap: {settings.SITE_URL}/sitemap.xml"])
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    entries = [(path, priority, changefreq, None) for path, priority, changefreq in STATIC_PAGES]
    for estate in Estate.objects.filter(is_published=True).only("slug", "created_at"):
        entries.append((
            estate.get_absolute_url(),
            "0.8",
            "weekly",
            estate.created_at.date().isoformat() if estate.created_at else None,
        ))

    urlset = ET.Element("urlset", xmlns=SITEMAP_NS)
    for path, priority, changefreq, lastmod in entries:
        node = ET.SubElement(urlset, "url")
        ET.SubElement(node, "loc").text = f"{settings.SITE_URL.rstrip('/')}{path}"
        if lastmod:
            ET.SubElement(node, "lastmod").text = lastmod
        ET.SubElement(node, "changefreq").text = changefreq
        ET.SubElement(node, "priority").text = priority

    ET.indent(urlset, space="  ")
    xml = ET.tostring(urlset, encoding="utf-8", xml_declaration=True)
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")
