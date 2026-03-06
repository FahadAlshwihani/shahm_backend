from rest_framework.response import Response


def api_response(success=True, message="", data=None, status_code=200):
    """
    Helper لتوحيد شكل ردود الـ API
    """
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)
