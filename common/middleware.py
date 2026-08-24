import traceback
from django.http import JsonResponse
from django.utils import timezone
from apps.core.models import Visit


class ErrorLoggingMiddleware:
    """
    Middleware يسجل الأخطاء ويرجع JSON نظيف
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            return self.get_response(request)

        except Exception as e:
            traceback.print_exc()

            return JsonResponse({
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=500)


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
