"""Rate limiting for plain Django views.

Django REST Framework views are throttled by the classes and rates configured
in ``config.settings.base``. Views that are plain Django views cannot use those
classes, so they use :func:`rate_limited`, which reads the same rate table and
the same client identity resolution.
"""

import time
from functools import wraps

from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.settings import api_settings
from rest_framework.throttling import BaseThrottle

PERIOD_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
}


def parse_rate(rate):
    """Return ``(limit, seconds)`` for a rate such as ``30/min``.

    Returns ``(None, None)`` when no rate is configured, which disables the
    limit rather than failing the request.
    """
    if not rate:
        return None, None

    count, _, period = str(rate).partition("/")

    try:
        return int(count), PERIOD_SECONDS[period[0]]
    except (ValueError, KeyError, IndexError):
        return None, None


def client_identifier(request):
    """Resolve the caller identity the same way DRF throttles resolve it."""
    return BaseThrottle().get_ident(request)


def is_rate_exceeded(scope, identifier):
    """Count one hit for ``identifier`` in ``scope`` and report the verdict."""
    limit, duration = parse_rate(
        api_settings.DEFAULT_THROTTLE_RATES.get(scope)
    )

    if not limit:
        return False

    window = int(time.time()) // duration
    key = f"throttle:{scope}:{identifier}:{window}"

    try:
        count = cache.incr(key)
    except ValueError:
        count = 1
        cache.set(key, count, duration + 1)

    return count > limit


def rate_limited(scope):
    """Apply the ``scope`` rate to a plain Django view."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            identifier = client_identifier(request)

            if is_rate_exceeded(scope, identifier):
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Request was throttled. Try again later.",
                    },
                    status=429,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
