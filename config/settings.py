from pathlib import Path
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _env(name, default=""):
    return os.environ.get(name, default).strip()


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Load variables from a local .env file (if present) without extra dependencies.
_env_path = BASE_DIR / ".env"
if _env_path.exists():
    with _env_path.open(encoding="utf-8") as _env_file:
        for _line in _env_file:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _key, _value = _line.split("=", 1)
            _key = _key.strip()
            _value = _value.strip().strip('"').strip("'")
            os.environ.setdefault(_key, _value)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# Render.com injects the public hostname of the service.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Support exposing the dev server through an ngrok tunnel.
CSRF_TRUSTED_ORIGINS = []
NGROK_URL = os.environ.get("NGROK_URL", "").strip()
if NGROK_URL:
    from urllib.parse import urlparse

    _parsed = urlparse(NGROK_URL if "://" in NGROK_URL else "https://" + NGROK_URL)
    if _parsed.hostname and _parsed.hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_parsed.hostname)
    CSRF_TRUSTED_ORIGINS.append(NGROK_URL.rstrip("/"))

# Render.com (and other) trusted origins from env or derived from the public hostname.
_extra_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _extra_csrf.split(",") if o.strip()])
if RENDER_EXTERNAL_HOSTNAME:
    _render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts", "catalog", "core", "base",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("fr", "Français"), ("it", "Italiano"), ("es", "Español")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

# --- Uploaded media storage -------------------------------------------------
# Static assets stay on local disk (WhiteNoise/Nginx). Uploaded media is served
# from an S3-compatible bucket when USE_S3_MEDIA=1, and from local disk
# otherwise (development default).
USE_S3_MEDIA = _env_bool("USE_S3_MEDIA", False)

S3_BUCKET_NAME = _env("S3_BUCKET_NAME")
S3_ACCESS_KEY_ID = _env("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = _env("S3_SECRET_ACCESS_KEY")
S3_REGION_NAME = _env("S3_REGION_NAME")
S3_ENDPOINT_URL = _env("S3_ENDPOINT_URL")
S3_CUSTOM_DOMAIN = _env("S3_CUSTOM_DOMAIN")
S3_LOCATION = _env("S3_LOCATION", "media")
S3_QUERYSTRING_AUTH = _env_bool("S3_QUERYSTRING_AUTH", False)
S3_DEFAULT_ACL = _env("S3_DEFAULT_ACL")

if USE_S3_MEDIA:
    if not S3_BUCKET_NAME:
        raise ImproperlyConfigured("USE_S3_MEDIA=1 requires S3_BUCKET_NAME")
    if bool(S3_ACCESS_KEY_ID) != bool(S3_SECRET_ACCESS_KEY):
        raise ImproperlyConfigured(
            "S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY must both be set, or neither "
            "(rely on an IAM instance role)."
        )

    _s3_options = {
        "bucket_name": S3_BUCKET_NAME,
        "location": S3_LOCATION,
        "default_acl": S3_DEFAULT_ACL or None,
        "querystring_auth": S3_QUERYSTRING_AUTH,
        "file_overwrite": _env_bool("S3_FILE_OVERWRITE", False),
        "object_parameters": {"CacheControl": "public, max-age=86400"},
    }
    if S3_ACCESS_KEY_ID:
        _s3_options["access_key"] = S3_ACCESS_KEY_ID
        _s3_options["secret_key"] = S3_SECRET_ACCESS_KEY
    if S3_REGION_NAME:
        _s3_options["region_name"] = S3_REGION_NAME
    if S3_ENDPOINT_URL:
        _s3_options["endpoint_url"] = S3_ENDPOINT_URL
    if S3_CUSTOM_DOMAIN:
        _s3_options["custom_domain"] = S3_CUSTOM_DOMAIN

    MEDIA_URL = f"https://{S3_CUSTOM_DOMAIN}/" if S3_CUSTOM_DOMAIN else "/media/"
    _default_storage = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": _s3_options,
    }
else:
    MEDIA_URL = "/media/"
    _default_storage = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": str(MEDIA_ROOT), "base_url": MEDIA_URL},
    }

STORAGES = {
    "default": _default_storage,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "base:home"
LOGOUT_REDIRECT_URL = "base:home"

if not DEBUG:
    if SECRET_KEY == "dev-only-change-before-deployment":
        raise RuntimeError("Set DJANGO_SECRET_KEY before deploying")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    USE_X_FORWARDED_HOST = True
    SECURE_HSTS_SECONDS = int(_env("DJANGO_HSTS_SECONDS", "31536000"))
    if SECURE_HSTS_SECONDS:
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# Log to stdout/stderr so systemd/journald (or the container runtime) can collect it.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "root": {"handlers": ["console"], "level": _env("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
