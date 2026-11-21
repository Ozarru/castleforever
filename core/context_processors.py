from pathlib import Path

from django.conf import settings

from .notifications import get_dashboard_notifications


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
