"""Temporary account lockout after repeated failed sign-in attempts.

Failures are counted per account, not per network address, so one mistyped
password cannot lock out every user sharing an office address. Address level
limiting is the ``login`` throttle scope configured in the REST settings.

Counters live in the default cache. A per-process cache counts them separately
in every worker; see the ``shahm.W001`` deployment check.
"""

from django.conf import settings
from django.core.cache import cache


def _key(email):
    return f"login-failures:{(email or '').strip().lower()}"


def failure_count(email):
    """Return the number of consecutive recent failures for ``email``."""
    return cache.get(_key(email), 0)


def is_locked(email):
    """Report whether ``email`` is currently locked out."""
    return failure_count(email) >= settings.LOGIN_FAILURE_LIMIT


def register_failure(email):
    """Count one failed attempt and return the new total."""
    key = _key(email)

    try:
        count = cache.incr(key)
    except ValueError:
        count = 1
        cache.set(key, count, settings.LOGIN_LOCKOUT_SECONDS)

    if count >= settings.LOGIN_FAILURE_LIMIT:
        # Hold the lock for its full duration from the most recent attempt.
        cache.touch(key, settings.LOGIN_LOCKOUT_SECONDS)

    return count


def clear(email):
    """Forget the failures recorded for ``email`` after a successful sign-in."""
    cache.delete(_key(email))
