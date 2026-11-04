"""
Django settings for the Lemon Courier insecure reference app.

This project is a coursework for the University of Helsinki course
"Introduction to Cyber Security: MOOC 2026" (TKT200094).
It CONTAINS DELIBERATE SECURITY FLAWS that are documented in the project report.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# FLAW 5 (A05 Security Misconfiguration): hard-coded SECRET_KEY, DEBUG=True, ALLOWED_HOSTS=*
SECRET_KEY = "lemon-courier-deliberately-insecure-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

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

# FIX (FLAW 5): load the key from the environment, turn DEBUG off, pin ALLOWED_HOSTS
# import os
# SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
# DEBUG = False
# ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# FIX (FLAW 5 / A09 also): log security-relevant events with a file handler
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {"security_log": {"class": "logging.FileHandler", "filename": "security.log"}},
#     "loggers": {"lemoncourier": {"handlers": ["security_log"], "level": "INFO"}},
# }
