from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User


class AuthenticationApiContractTests(TestCase):
    password = "Release-Test-Password-123!"

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.test",
            password=self.password,
            name="Admin",
            role="admin",
        )
        self.editor = User.objects.create_user(
            email="editor@example.test",
            password=self.password,
            name="Editor",
            role="editor",
        )

    def login(self, user):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        return response

    def authenticate(self, user):
        access = self.login(user).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_login_returns_user_access_and_refresh_contract(self):
        response = self.login(self.admin)

        self.assertEqual(response.data["user"]["email"], self.admin.email)
        self.assertEqual(response.data["user"]["role"], "admin")
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])

    def test_invalid_login_returns_401(self):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": self.admin.email, "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"], "Invalid email or password")

    def test_refresh_returns_new_access_token_and_rejects_invalid_token(self):
        refresh = self.login(self.admin).data["refresh"]

        valid = self.client.post(
            "/api/accounts/refresh/",
            {"refresh": refresh},
            format="json",
        )
        invalid = self.client.post(
            "/api/accounts/refresh/",
            {"refresh": "not-a-jwt"},
            format="json",
        )

        self.assertEqual(valid.status_code, 200)
        self.assertTrue(valid.data["access"])
        self.assertEqual(invalid.status_code, 401)

    def test_protected_endpoint_rejects_missing_and_invalid_access_tokens(self):
        missing = self.client.get("/api/accounts/users/")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        invalid = self.client.get("/api/accounts/users/")

        self.assertEqual(missing.status_code, 401)
        self.assertEqual(invalid.status_code, 401)

    def test_editor_cannot_manage_users_but_admin_can_list_them(self):
        self.authenticate(self.editor)
        forbidden = self.client.get("/api/accounts/users/")

        self.client.credentials()
        self.authenticate(self.admin)
        allowed = self.client.get("/api/accounts/users/")

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(
            {item["email"] for item in allowed.data},
            {self.admin.email, self.editor.email},
        )

    def test_admin_can_create_update_and_delete_user(self):
        self.authenticate(self.admin)
        created = self.client.post(
            "/api/accounts/users/create/",
            {
                "email": "viewer@example.test",
                "name": "Viewer",
                "role": "viewer",
                "password": self.password,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)

        user_id = created.data["id"]
        updated = self.client.patch(
            f"/api/accounts/users/{user_id}/",
            {"name": "Updated Viewer"},
            format="json",
        )
        deleted = self.client.delete(f"/api/accounts/users/{user_id}/")

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["name"], "Updated Viewer")
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse(User.objects.filter(pk=user_id).exists())
