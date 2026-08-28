import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response

from common.logging import get_request_id

logger = logging.getLogger("shahm.api")


def custom_exception_handler(exc, context):
    """
    Custom Error Response Handler

    Exceptions that DRF cannot map to a response are logged in full and
    answered with a stable error code plus the request identifier. The
    exception text is never returned to the client.
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.error(
            "Unhandled API exception in %s",
            context.get("view"),
            exc_info=exc,
        )

        return Response({
            "success": False,
            "message": "Unknown server error occurred.",
            "error": "internal_error",
            "request_id": get_request_id(),
        }, status=500)

    return Response({
        "success": False,
        "message": response.data.get("detail", "An error occurred."),
        "errors": response.data
    }, status=response.status_code)
