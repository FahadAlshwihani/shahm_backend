from apps.services.request_access import (
    ServiceRequestAccessActivity,
)


class AccessActivityService:

    @staticmethod
    def log(
        request,
        link,
        action,
        metadata=None,
    ):

        forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        ip = None

        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()

        else:
            ip = request.META.get(
                "REMOTE_ADDR"
            )

        payload = {
            "action": action,
            "ip_address": ip,
            "user_agent": request.META.get(
                "HTTP_USER_AGENT",
                "",
            ),
            "metadata": metadata or {},
        }

        if link:
            payload["link"] = link

        ServiceRequestAccessActivity.objects.create(
            **payload
        )