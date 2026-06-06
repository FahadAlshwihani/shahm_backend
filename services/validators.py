import os
import mimetypes

from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 20 * 1024 * 1024

BLOCKED_MIMES = [
    "application/x-msdownload",
    "application/x-sh",
    "application/x-bat",
    "text/html",
    "image/svg+xml",
]

FILE_EXTENSION_MIME_MAP = {
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".png": ["image/png"],
    ".pdf": ["application/pdf"],
    ".doc": ["application/msword"],
    ".docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ],
    ".mp3": ["audio/mpeg"],
    ".wav": ["audio/wav"],
}

PDF_SIGNATURE = b"%PDF"


# =========================================================
# LEGACY DJANGO MODEL VALIDATOR
# =========================================================
def validate_file(uploaded_file):
    """
    Backward compatibility validator for old migrations/models.
    """
    validate_uploaded_file(uploaded_file)


# =========================================================
# MAIN VALIDATOR
# =========================================================
def validate_uploaded_file(
    uploaded_file,
    allowed_extensions=None,
    max_size_mb=20,
):
    if not uploaded_file:
        return

    max_size_bytes = max_size_mb * 1024 * 1024

    if uploaded_file.size > max_size_bytes:
        raise ValidationError(
            f"File size must not exceed {max_size_mb}MB."
        )

    filename = uploaded_file.name.lower()

    extension = os.path.splitext(filename)[1].lower()

    # ============================================
    # EXTENSION VALIDATION
    # ============================================

    if allowed_extensions:
        normalized_extensions = [
            ext.lower()
            if ext.startswith(".")
            else f".{ext.lower()}"
            for ext in allowed_extensions
        ]

        if extension not in normalized_extensions:
            raise ValidationError(
                "File extension is not allowed."
            )

    else:
        normalized_extensions = list(
            FILE_EXTENSION_MIME_MAP.keys()
        )

    # ============================================
    # MIME VALIDATION
    # ============================================

    detected_mime = (
        uploaded_file.content_type or ""
    ).lower()

    allowed_mimes = set()

    for ext in normalized_extensions:
        mime_list = FILE_EXTENSION_MIME_MAP.get(
            ext,
            [],
        )

        for mime in mime_list:
            allowed_mimes.add(mime.lower())

    if (
        allowed_mimes
        and detected_mime not in allowed_mimes
    ):
        raise ValidationError(
            "Unsupported file type."
        )

    if detected_mime in BLOCKED_MIMES:
        raise ValidationError(
            "This MIME type is blocked."
        )

    # ============================================
    # FILE SIGNATURE VALIDATION
    # ============================================

    uploaded_file.seek(0)

    file_signature = uploaded_file.read(16)

    uploaded_file.seek(0)

    if extension == ".pdf":
        if not file_signature.startswith(
            PDF_SIGNATURE
        ):
            raise ValidationError(
                "Invalid PDF file."
            )

    # ============================================
    # MIME CATEGORY VALIDATION
    # ============================================

    guessed_mime, _ = mimetypes.guess_type(
        uploaded_file.name
    )

    if guessed_mime and detected_mime:

        guessed_main = (
            guessed_mime.split("/")[0]
        )

        detected_main = (
            detected_mime.split("/")[0]
        )

        if guessed_main != detected_main:
            raise ValidationError(
                "File MIME type mismatch."
            )