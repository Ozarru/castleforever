from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import set_language
from accounts import views as account_views

urlpatterns = [
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
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.urls import re_path
    from django.views.static import serve as media_serve

    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}),
    ]
