"""Select secure production or development settings from ``DEBUG``."""

from .base import *  # noqa: F401,F403

if DEBUG:  # noqa: F405
    from .development import *  # noqa: F401,F403
else:
    from .production import *  # noqa: F401,F403
