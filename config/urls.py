from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve as media_serve

from accounts import views as account_views


def healthz(request):
    """Lightweight readiness probe used by Nginx/systemd checks."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("profile/", account_views.profile, name="profile"),
    path("notifications/", account_views.notifications, name="notifications"),
    path("activity/", account_views.activity, name="activity"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("base.urls")),
    path("", include("catalog.urls")),
    path("", include("core.urls")),
]

# Uploaded media is served by the bucket when USE_S3_MEDIA=1. Local disk is only
# used as a fallback (development, or a VPS without an object store).
if settings.USE_S3_MEDIA:
    pass
elif settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}),
    ]
