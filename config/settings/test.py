"""Isolated settings for the automated Django test suite."""

from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Throttling stays switched on so the wiring is exercised, but the shared
# in-memory counters are not reset between tests. Contract tests therefore run
# against rates they cannot reach; the throttling tests set their own rates.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {
        scope: "10000/min"
        for scope in REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]  # noqa: F405
    },
}

# Keep the suite output readable. Records still reach assertLogs, which
# installs its own handler, so logging behaviour stays testable.
LOGGING = {
    **LOGGING,  # noqa: F405
    "handlers": {
        name: {**config, "level": "CRITICAL"}
        for name, config in LOGGING["handlers"].items()  # noqa: F405
    },
}

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
