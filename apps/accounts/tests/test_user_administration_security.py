"""Role boundaries for the dashboard user administration endpoints."""

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.guards import leaves_no_active_super_admin
from apps.accounts.models import User


class UserAdministrationSecurityTests(TestCase):
    password = "Release-Test-Password-123!"

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.super_admin = User.objects.create_user(
            email="super@example.test",
            password=self.password,
            name="Super",
            role="super_admin",
        )
        self.admin = User.objects.create_user(
            email="admin@example.test",
            password=self.password,
            name="Admin",
            role="admin",
        )

    def tearDown(self):
        cache.clear()

    def authenticate(self, user):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_admin_cannot_create_a_super_admin(self):
        self.authenticate(self.admin)

        response = self.client.post(
            "/api/accounts/users/create/",
            {
                "email": "escalated@example.test",
                "name": "Escalated",
                "role": "super_admin",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data)
        self.assertFalse(User.objects.filter(email="escalated@example.test").exists())

    def test_admin_cannot_promote_themselves(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            f"/api/accounts/users/{self.admin.pk}/",
            {"role": "super_admin"},
            format="json",
        )

        self.admin.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.admin.role, "admin")

    def test_admin_cannot_edit_or_delete_a_super_admin(self):
        self.authenticate(self.admin)

        patched = self.client.patch(
            f"/api/accounts/users/{self.super_admin.pk}/",
            {"is_active": False},
            format="json",
        )
        deleted = self.client.delete(f"/api/accounts/users/{self.super_admin.pk}/")

        self.super_admin.refresh_from_db()

        self.assertEqual(patched.status_code, 403)
        self.assertEqual(deleted.status_code, 403)
        self.assertTrue(self.super_admin.is_active)
        self.assertTrue(User.objects.filter(pk=self.super_admin.pk).exists())

    def test_admin_keeps_managing_lower_roles(self):
        self.authenticate(self.admin)

        created = self.client.post(
            "/api/accounts/users/create/",
            {
                "email": "editor@example.test",
                "name": "Editor",
                "role": "editor",
                "password": self.password,
            },
            format="json",
        )
        updated = self.client.patch(
            f"/api/accounts/users/{created.data['id']}/",
            {"name": "Renamed Editor"},
            format="json",
        )
        deleted = self.client.delete(f"/api/accounts/users/{created.data['id']}/")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(deleted.status_code, 200)

    def test_nobody_can_delete_their_own_account(self):
        self.authenticate(self.super_admin)

        response = self.client.delete(f"/api/accounts/users/{self.super_admin.pk}/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.super_admin.pk).exists())

    def test_the_last_super_admin_cannot_be_deactivated(self):
        self.authenticate(self.super_admin)

        response = self.client.patch(
            f"/api/accounts/users/{self.super_admin.pk}/",
            {"is_active": False},
            format="json",
        )

        self.super_admin.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.super_admin.is_active)

    def test_a_super_admin_may_be_deactivated_while_another_remains(self):
        second_super = User.objects.create_user(
            email="super2@example.test",
            password=self.password,
            name="Second Super",
            role="super_admin",
        )
        self.authenticate(self.super_admin)

        response = self.client.patch(
            f"/api/accounts/users/{second_super.pk}/",
            {"is_active": False},
            format="json",
        )

        second_super.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(second_super.is_active)

    def test_removal_guard_reports_the_last_active_super_admin(self):
        inactive_super = User.objects.create_user(
            email="dormant@example.test",
            password=self.password,
            name="Dormant Super",
            role="super_admin",
            is_active=False,
        )

        self.assertTrue(leaves_no_active_super_admin(self.super_admin))
        self.assertFalse(leaves_no_active_super_admin(inactive_super))
        self.assertFalse(leaves_no_active_super_admin(self.admin))

    def test_super_admin_may_still_assign_any_role(self):
        self.authenticate(self.super_admin)

        response = self.client.post(
            "/api/accounts/users/create/",
            {
                "email": "second-super@example.test",
                "name": "Second Super",
                "role": "super_admin",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["role"], "super_admin")

    def test_nobody_can_change_their_own_role(self):
        self.authenticate(self.super_admin)

        response = self.client.patch(
            f"/api/accounts/users/{self.super_admin.pk}/",
            {"role": "admin"},
            format="json",
        )

        self.super_admin.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.super_admin.role, "super_admin")
