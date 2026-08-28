"""Deployment checks for settings that fail silently in production."""

from django.conf import settings
from django.core.checks import Tags, Warning, register

PER_PROCESS_CACHE_BACKENDS = (
    "django.core.cache.backends.locmem.LocMemCache",
    "django.core.cache.backends.dummy.DummyCache",
)


@register(Tags.caches, deploy=True)
def check_throttle_cache_is_shared(app_configs, **kwargs):
    """Warn when rate limiting cannot be enforced across worker processes."""
    backend = (
        settings.CACHES.get("default", {}).get("BACKEND", "")
    )

    if backend not in PER_PROCESS_CACHE_BACKENDS:
        return []

    return [
        Warning(
            "The default cache is per-process, so login, OTP and public form "
            "rate limits are counted separately in every worker.",
            hint=(
                "Set CACHE_URL to a shared cache before serving with more "
                "than one worker process."
            ),
            id="shahm.W001",
        )
    ]
