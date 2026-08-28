"""Public endpoints that were reachable without any rate limit."""

from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.cms.views import public_search
from common.checks import check_throttle_cache_is_shared
from common.throttling import parse_rate

SHARED_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/shahm-test-cache",
    }
}


class RateParsingTests(SimpleTestCase):
    def test_known_and_unknown_rates(self):
        self.assertEqual(parse_rate("30/min"), (30, 60))
        self.assertEqual(parse_rate("5/s"), (5, 1))
        self.assertEqual(parse_rate("2/hour"), (2, 3600))
        self.assertEqual(parse_rate(None), (None, None))
        self.assertEqual(parse_rate("nonsense"), (None, None))


class PublicSearchThrottleTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def request(self):
        # A one character query returns before any database work, so this
        # exercises the limiter itself rather than the search.
        return public_search(
            RequestFactory().get("/api/cms/public/search/", {"q": "a"})
        )

    def test_search_is_limited_and_keeps_its_success_contract(self):
        with self.settings(
            REST_FRAMEWORK={
                **self.rest_framework_settings(),
                "DEFAULT_THROTTLE_RATES": {"search": "2/min"},
            }
        ):
            statuses = [self.request().status_code for _ in range(3)]

        self.assertEqual(statuses, [200, 200, 429])

    def test_missing_rate_leaves_the_endpoint_open(self):
        with self.settings(
            REST_FRAMEWORK={
                **self.rest_framework_settings(),
                "DEFAULT_THROTTLE_RATES": {},
            }
        ):
            statuses = [self.request().status_code for _ in range(3)]

        self.assertEqual(statuses, [200, 200, 200])

    @staticmethod
    def rest_framework_settings():
        from django.conf import settings

        return dict(settings.REST_FRAMEWORK)


class ThrottleCacheCheckTests(SimpleTestCase):
    def test_per_process_cache_is_reported(self):
        warnings = check_throttle_cache_is_shared(None)

        self.assertEqual([warning.id for warning in warnings], ["shahm.W001"])

    @override_settings(CACHES=SHARED_CACHE)
    def test_shared_cache_is_accepted(self):
        self.assertEqual(check_throttle_cache_is_shared(None), [])
