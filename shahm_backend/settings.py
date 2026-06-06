# settings.py

from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-tx+!c&8)8t+)*m8mu*)%mi%e&8%t36kn&9!&_vfkhph*r@bot2"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ===========================
# INSTALLED APPS
# ===========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",

    # Third Party
    "rest_framework",
    "corsheaders",

    # Project
    "accounts",
    "core",
    "cms.apps.CmsConfig",
    "blog",
    "team",
    "services",
    "legal",
    "messaging",
    "settings_app.apps.SettingsAppConfig",
    "seo",
    "form_builder",
    'django_filters',
]

# ===========================
# MIDDLEWARE
# ===========================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    # Error Logging
    "core.middleware.ErrorLoggingMiddleware",

    # Django Auth
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Visitor Tracking (بعد Authentication)
    "core.middleware.VisitorTrackingMiddleware",
]

ROOT_URLCONF = "shahm_backend.urls"

# ===========================
# TEMPLATES
# ===========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "shahm_backend.wsgi.application"

# ===========================
# AUTH
# ===========================

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_THROTTLE_CLASSES": [],

    "DEFAULT_THROTTLE_RATES": {
        "otp": "5/min",
        "login": "10/min",
        "search": "30/min",
    },

    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",

    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
}

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": False,

    "BLACKLIST_AFTER_ROTATION": False,

    "UPDATE_LAST_LOGIN": True,

    "AUTH_HEADER_TYPES": ("Bearer",),

}

# ===========================
# DATABASE
# ===========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ===========================
# AUTH PASSWORD
# ===========================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===========================
# I18N
# ===========================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Riyadh"

USE_I18N = True
USE_TZ = True

# ===========================
# STATIC & MEDIA
# ===========================

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"  # <<<<< مهم جداً

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ===========================
# FILE UPLOAD SETTINGS (IMPORTANT FOR VIDEO)
# ===========================

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# ===========================
# CORS
# ===========================
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(
    default_headers
) + [
                         "x-access-token",
                     ]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://127.0.0.1:8000"

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#     }
# }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
