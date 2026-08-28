"""Request correlation identifiers shared by middleware, logging and errors.

Error responses no longer expose exception text. They expose a short request
identifier instead, and the same identifier is written to the application log,
so an operator can find the failing request without the client ever seeing
internal details.
"""

import contextvars
import logging
import uuid

_request_id = contextvars.ContextVar("request_id", default="-")


def new_request_id():
    """Return a short identifier for one request."""
    return uuid.uuid4().hex[:12]


def set_request_id(value):
    """Bind ``value`` to the current context and return the reset token."""
    return _request_id.set(value)


def reset_request_id(token):
    """Restore the previous identifier bound to this context."""
    _request_id.reset(token)


def get_request_id():
    """Return the identifier of the request being handled, or ``-``."""
    return _request_id.get()


class RequestIdFilter(logging.Filter):
    """Add ``request_id`` to every record so log formats can reference it."""

    def filter(self, record):
        record.request_id = get_request_id()
        return True
