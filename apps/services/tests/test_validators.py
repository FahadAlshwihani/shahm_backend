from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from apps.services.validators import validate_uploaded_file


class UploadValidatorTests(SimpleTestCase):
    def test_rejects_jpeg_extension_with_invalid_signature(self):
        uploaded = SimpleUploadedFile(
            "photo.jpg",
            b"not-a-jpeg",
            content_type="image/jpeg",
        )

        with self.assertRaisesMessage(ValidationError, "Invalid JPEG file"):
            validate_uploaded_file(uploaded)

    def test_accepts_png_with_valid_signature(self):
        uploaded = SimpleUploadedFile(
            "image.png",
            b"\x89PNG\r\n\x1a\n" + b"content",
            content_type="image/png",
        )

        validate_uploaded_file(uploaded)
