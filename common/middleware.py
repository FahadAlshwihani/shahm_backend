import logging

from django.http import JsonResponse
from django.utils import timezone
from apps.core.models import Visit

from common.logging import (
    get_request_id,
    new_request_id,
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger("shahm.request")


class ErrorLoggingMiddleware:
    """
    Middleware يسجل الأخطاء ويرجع JSON نظيف

    The exception text is written to the application log only. The client
    receives a stable error code and the request identifier that the log entry
    carries, so support can trace a failure without internal details leaving
    the server.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        token = set_request_id(new_request_id())

        try:
            response = self.get_response(request)

        except Exception:
            logger.exception(
                "Unhandled error while serving %s %s",
                request.method,
                request.path,
            )

            response = JsonResponse({
                "success": False,
                "message": "Internal server error",
                "error": "internal_error",
                "request_id": get_request_id(),
            }, status=500)

        response["X-Request-ID"] = get_request_id()
        reset_request_id(token)

        return response


class VisitorTrackingMiddleware:
    """
    يسجل زيارات الموقع:
    - IP
    - User Agent
    - Path
    - Timestamp
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # تجاهل admin بالكامل
        if request.path.startswith("/admin"):
            return self.get_response(request)

        # تجاهل API الخاصة بالـ backend (لا نريد تسجيلها)
        if request.path.startswith("/api/core"):
            return self.get_response(request)

        # السماح بـ /api/public لأنها تستدعى من الواجهة
        # لكن لا نسجلها كزيارة لأنها ليست صفحة
        if request.path.startswith("/api/public"):
            return self.get_response(request)

        # تجاهل static/media
        if request.path.startswith("/static") or request.path.startswith("/media"):
            return self.get_response(request)

        # -----------------------------
        # تسجيل الزيارة
        # -----------------------------
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]
        path = request.get_full_path()

        Visit.objects.create(
            ip_address=ip,
            user_agent=ua,
            path=path,
            visited_at=timezone.now(),
        )

        return self.get_response(request)
