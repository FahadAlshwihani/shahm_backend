from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class AccountUrlTests(SimpleTestCase):
    def test_refresh_endpoint_is_registered(self):
        match = resolve("/api/accounts/refresh/")

        self.assertEqual(match.url_name, "token-refresh")

    def test_initial_admin_setup_is_disabled_by_default(self):
        with self.assertRaises(Resolver404):
            resolve("/api/accounts/super/init/")
