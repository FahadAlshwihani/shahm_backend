"""Sign-in hardening: enumeration, lockout and rate limiting."""

from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework.throttling import SimpleRateThrottle

from apps.accounts.models import User


class LoginSecurityTests(TestCase):
    password = "Release-Test-Password-123!"

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="member@example.test",
            password=self.password,
            name="Member",
            role="editor",
        )

    def tearDown(self):
        cache.clear()

    def login(self, email, password):
        return self.client.post(
            "/api/accounts/login/",
            {"email": email, "password": password},
            format="json",
        )

    def test_unknown_email_and_wrong_password_are_indistinguishable(self):
        unknown = self.login("nobody@example.test", "whatever")
        wrong = self.login(self.user.email, "whatever")

        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(wrong.status_code, 401)
        self.assertEqual(unknown.data, wrong.data)

    def test_unknown_email_still_runs_the_password_hasher(self):
        """The dummy hash is what removes the timing oracle."""
        with patch.object(User, "set_password", autospec=True) as dummy_hash:
            self.login("nobody@example.test", "whatever")

        self.assertTrue(dummy_hash.called)

    @override_settings(LOGIN_FAILURE_LIMIT=3, LOGIN_LOCKOUT_SECONDS=60)
    def test_account_locks_after_repeated_failures(self):
        for _ in range(3):
            self.assertEqual(self.login(self.user.email, "wrong").status_code, 401)

        locked = self.login(self.user.email, "wrong")
        locked_with_correct_password = self.login(self.user.email, self.password)

        self.assertEqual(locked.status_code, 429)
        self.assertEqual(locked_with_correct_password.status_code, 429)

    @override_settings(LOGIN_FAILURE_LIMIT=3, LOGIN_LOCKOUT_SECONDS=60)
    def test_successful_login_clears_the_failure_counter(self):
        self.login(self.user.email, "wrong")
        self.login(self.user.email, "wrong")

        self.assertEqual(self.login(self.user.email, self.password).status_code, 200)

        for _ in range(3):
            self.assertEqual(self.login(self.user.email, "wrong").status_code, 401)

    def test_disabled_account_keeps_its_403_contract(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.login(self.user.email, self.password)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["error"], "Account disabled")

    def test_missing_credentials_do_not_reach_the_backend(self):
        self.assertEqual(self.login("", "").status_code, 401)
        self.assertEqual(self.login(self.user.email, "").status_code, 401)

    def test_login_endpoint_is_rate_limited_per_address(self):
        # DRF binds the rate table to the throttle class at import time, so the
        # rate is patched there rather than through the settings dictionary.
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, {"login": "2/min"}):
            statuses = [
                self.login(self.user.email, self.password).status_code
                for _ in range(3)
            ]

        self.assertEqual(statuses[:2], [200, 200])
        self.assertEqual(statuses[2], 429)

    def test_scoped_throttling_is_actually_enabled(self):
        """The rate table is inert unless the throttle class is registered."""
        from rest_framework.settings import api_settings
        from rest_framework.throttling import ScopedRateThrottle

        self.assertIn(ScopedRateThrottle, api_settings.DEFAULT_THROTTLE_CLASSES)
