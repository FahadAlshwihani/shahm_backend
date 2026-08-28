from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import LoginView, UsersListView
from apps.cms.views import public_search


class AuthenticationContractTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("apps.accounts.views.authenticate", return_value=None)
    @patch("apps.accounts.views.User.objects.filter")
    def test_invalid_login_returns_401(self, user_filter, _authenticate):
        user_filter.return_value.first.return_value = None
        request = self.factory.post(
            "/api/accounts/login/",
            {"email": "missing@example.com", "password": "invalid"},
            format="json",
        )

        response = LoginView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_valid_refresh_token_returns_access_token(self):
        refresh = RefreshToken()
        request = self.factory.post(
            "/api/accounts/refresh/",
            {"refresh": str(refresh)},
            format="json",
        )

        response = TokenRefreshView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_protected_users_endpoint_without_jwt_returns_401(self):
        request = self.factory.get("/api/accounts/users/")

        response = UsersListView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_editor_role_cannot_access_admin_user_list(self):
        request = self.factory.get("/api/accounts/users/")
        force_authenticate(
            request,
            user=SimpleNamespace(is_authenticated=True, role="editor"),
        )

        response = UsersListView.as_view()(request)

        self.assertEqual(response.status_code, 403)


class PublicSearchContractTests(SimpleTestCase):
    def test_short_search_query_returns_empty_200_response(self):
        request = RequestFactory().get(
            "/api/cms/public/search/",
            {"q": "a", "lang": "en"},
        )

        response = public_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])
