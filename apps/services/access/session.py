import jwt

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from django.conf import settings

from rest_framework.exceptions import (
    PermissionDenied,
)


ACCESS_SESSION_EXPIRY_MINUTES = 30


class AccessSessionService:

    @classmethod
    def generate_token(
        cls,
        public_key,
    ):

        payload = {
            "public_key": public_key,
            "type": "request_access",
            "exp": (
                datetime.now(
                    timezone.utc
                )
                + timedelta(
                    minutes=ACCESS_SESSION_EXPIRY_MINUTES
                )
            ),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

    @classmethod
    def validate_token(
        cls,
        public_key,
        token,
    ):

        if not token:
            raise PermissionDenied(
                "Access token missing."
            )

        try:

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

        except jwt.ExpiredSignatureError:
            raise PermissionDenied(
                "Access token expired."
            )

        except jwt.InvalidTokenError:
            raise PermissionDenied(
                "Invalid access token."
            )

        if payload.get("type") != "request_access":
            raise PermissionDenied(
                "Invalid token type."
            )

        if payload.get("public_key") != public_key:
            raise PermissionDenied(
                "Token mismatch."
            )

        return payload