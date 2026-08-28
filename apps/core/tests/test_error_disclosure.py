"""Server errors must not carry exception text back to the client."""

import logging

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from common.exceptions import custom_exception_handler
from common.logging import get_request_id
from common.middleware import ErrorLoggingMiddleware

SECRET = "Access denied for user 'shahm'@'localhost' using password YES"


class ErrorDisclosureTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_middleware_hides_the_exception_and_logs_it(self):
        def boom(request):
            raise RuntimeError(SECRET)

        middleware = ErrorLoggingMiddleware(boom)

        with self.assertLogs("shahm.request", level=logging.ERROR) as logs:
            response = middleware(self.factory.get("/anything/"))

        body = response.content.decode()

        self.assertEqual(response.status_code, 500)
        self.assertNotIn(SECRET, body)
        self.assertIn("internal_error", body)
        self.assertTrue(response["X-Request-ID"])
        self.assertIn(SECRET, "\n".join(logs.output))

    def test_exception_handler_hides_the_exception_and_logs_it(self):
        with self.assertLogs("shahm.api", level=logging.ERROR) as logs:
            response = custom_exception_handler(
                RuntimeError(SECRET),
                {"view": "DummyView"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn(SECRET, str(response.data))
        self.assertEqual(response.data["error"], "internal_error")
        self.assertIn(SECRET, "\n".join(logs.output))

    def test_successful_responses_carry_a_request_identifier(self):
        seen = {}

        def view(request):
            seen["request_id"] = get_request_id()
            return HttpResponse("ok")

        response = ErrorLoggingMiddleware(view)(self.factory.get("/anything/"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Request-ID"], seen["request_id"])
        self.assertNotEqual(seen["request_id"], "-")
