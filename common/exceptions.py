from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom Error Response Handler
    """
    response = exception_handler(exc, context)

    if response is None:
        return Response({
            "success": False,
            "message": "Unknown server error occurred.",
            "error": str(exc),
        }, status=500)

    return Response({
        "success": False,
        "message": response.data.get("detail", "An error occurred."),
        "errors": response.data
    }, status=response.status_code)
