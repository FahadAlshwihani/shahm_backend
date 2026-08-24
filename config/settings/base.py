from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

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
    "apps.accounts.apps.AccountsConfig",
    "apps.core.apps.CoreConfig",
    "apps.cms.apps.CmsConfig",
    "apps.blog.apps.BlogConfig",
    "apps.team.apps.TeamConfig",
    "apps.services.apps.ServicesConfig",
    "apps.legal.apps.LegalConfig",
    "apps.messaging.apps.MessagingConfig",
    "apps.settings_app.apps.SettingsAppConfig",
    "apps.seo.apps.SeoConfig",
    "apps.form_builder.apps.FormBuilderConfig",
    'django_filters',
]

# ===========================
# MIDDLEWARE
# ===========================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    # Error Logging
    "common.middleware.ErrorLoggingMiddleware",

    # Django Auth
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Visitor Tracking (بعد Authentication)
    "common.middleware.VisitorTrackingMiddleware",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

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

    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",

    "DEFAULT_PAGINATION_CLASS": "common.pagination.DefaultPagination",
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
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
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
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


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
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[env("FRONTEND_URL")])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

CORS_ALLOW_HEADERS = list(
    default_headers
) + [
                         "x-access-token",
                     ]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FRONTEND_URL = env("FRONTEND_URL")
BACKEND_URL = env("BACKEND_URL")
SITE_URL = env("SITE_URL", default=FRONTEND_URL).rstrip("/")

# Disabled by default; operators may enable the one-time bootstrap URL only
# during a controlled initial deployment window.
ENABLE_INITIAL_ADMIN_SETUP = env.bool(
    "ENABLE_INITIAL_ADMIN_SETUP",
    default=False,
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

STATICFILES_DIRS = [
    BASE_DIR / "static",
] if (BASE_DIR / "static").exists() else []
