"""
Django settings for the SECURE (fix) version of the Lemon Courier app.

The fixes for FLAW 5 (A05 Security Misconfiguration) are APPLIED here:
env-based SECRET_KEY, DEBUG=False, pinned ALLOWED_HOSTS, LOGGING for A09.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# FIXED (FLAW 5): env-based SECRET_KEY, DEBUG off, ALLOWED_HOSTS pinned, plus A09 logging
import os
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "0000000000000000000000000000000000000000000000000000000000")
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "flawapp",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "csbproj.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "csbproj.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# FIXED (FLAW 5): env-based SECRET_KEY, DEBUG off, ALLOWED_HOSTS pinned, plus A09 logging
import os
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "0000000000000000000000000000000000000000000000000000000000")
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"security_log": {"class": "logging.FileHandler", "filename": "security.log"}},
    "loggers": {"lemoncourier": {"handlers": ["security_log"], "level": "INFO"}},
}
