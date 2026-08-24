import json

from django.conf import settings
from django.test import TestCase
from django.urls import resolve
from django.utils.module_loading import import_string
from rest_framework.test import APIClient


class ReleaseRouteContractTests(TestCase):
    public_routes = [
        ("/api/public/header/", "apps.core.views_public.PublicHeaderView"),
        ("/api/public/footer/", "apps.core.views_public.PublicFooterView"),
        ("/api/cms/public/home/", "apps.cms.views.PublicHomeView"),
        ("/api/cms/public/about/", "apps.cms.views.PublicAboutView"),
        ("/api/cms/public/faq/", "apps.cms.views.PublicFAQView"),
        ("/api/cms/public/search/", "apps.cms.views.public_search"),
        ("/api/blog/posts/", "apps.blog.views.PublicBlogListView"),
        ("/api/blog/settings/", "apps.blog.views.PublicBlogSettingsView"),
        ("/api/legal/page/privacy/", "apps.legal.views.PublicLegalPageView"),
        ("/api/seo/public/", "apps.seo.views.PublicSEOView"),
        ("/api/services/public/services/", "apps.services.views.PublicServiceViewSet"),
        ("/api/services/public/careers/jobs/", "apps.services.views.PublicCareerJobsViewSet"),
        ("/api/services/public/appointments/slots/", "apps.services.appointments.public_views.PublicAvailableSlotsView"),
        ("/api/public/forms/example/", "apps.form_builder.views.PublicFormDetailView"),
    ]

    admin_routes = [
        ("/api/accounts/users/", "apps.accounts.views.UsersListView"),
        ("/api/cms/admin/heroes/", "apps.cms.views.HeroListCreateView"),
        ("/api/cms/admin/header/", "apps.cms.views.HeaderLinkListCreateView"),
        ("/api/cms/admin/footer/settings/", "apps.cms.views.FooterSettingsView"),
        ("/api/cms/admin/about/", "apps.cms.views.AdminAboutView"),
        ("/api/cms/admin/faq/", "apps.cms.views.FAQListCreateView"),
        ("/api/blog/admin/posts/", "apps.blog.views.BlogListCreateView"),
        ("/api/legal/admin/pages/", "apps.legal.views.LegalPageListCreateView"),
        ("/api/seo/admin/default/", "apps.seo.views.DefaultSEOView"),
        ("/api/settings/", "apps.settings_app.views.SiteSettingsView"),
        ("/api/settings/email/", "apps.settings_app.views.EmailSettingsView"),
        ("/api/messaging/admin/messages/", "apps.messaging.views.AdminMessagesView"),
        ("/api/admin/forms/", "apps.form_builder.views.AdminFormTemplateListCreateView"),
        ("/api/services/admin/services/", "apps.services.views.AdminServiceViewSet"),
        ("/api/services/admin/careers/applications/", "apps.services.views.AdminCareerApplicationsViewSet"),
        ("/api/services/admin/appointments/bookings/", "apps.services.appointments.admin_views.AdminAppointmentBookingsView"),
        ("/api/services/admin/service-advisory-requests/1/access-links/create/", "apps.services.access.views.AdminCreateAccessLinkView"),
    ]

    @staticmethod
    def resolved_view(path):
        callback = resolve(path).func
        view_class = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
        if view_class:
            return view_class, f"{view_class.__module__}.{view_class.__name__}"
        return callback, f"{callback.__module__}.{callback.__name__}"

    def test_public_domain_routes_resolve_to_current_apps_modules(self):
        for path, expected_view in self.public_routes:
            with self.subTest(path=path):
                view, actual_view = self.resolved_view(path)
                self.assertEqual(actual_view, expected_view)
                if expected_view == "apps.cms.views.public_search":
                    self.assertFalse(hasattr(view, "permission_classes"))
                else:
                    permissions = {
                        permission.__name__
                        for permission in getattr(view, "permission_classes", [])
                    }
                    self.assertIn("AllowAny", permissions)

    def test_admin_domain_routes_resolve_and_require_authentication(self):
        client = APIClient()

        for path, expected_view in self.admin_routes:
            with self.subTest(path=path):
                _, actual_view = self.resolved_view(path)
                self.assertEqual(actual_view, expected_view)
                response = client.get(path)
                self.assertEqual(response.status_code, 401)

    def test_committed_frontend_contract_inventory_targets_importable_views(self):
        matrix_path = settings.BASE_DIR / "docs" / "API_CONTRACT_MATRIX.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

        self.assertEqual(matrix["frontend_request_count"], 219)
        self.assertEqual(
            matrix["summary"], {"MATCH": 219, "MISMATCH": 0, "UNCERTAIN": 0}
        )
        self.assertEqual(matrix["unique_frontend_contract_count"], 168)
        self.assertEqual(len(matrix["frontend_requests"]), 168)
        for contract in matrix["frontend_requests"]:
            with self.subTest(contract=f"{contract['module']}::{contract['function']}"):
                self.assertEqual(contract["result"], "MATCH")
                import_string(contract["view"])


class PublicDomainHttpContractTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_empty_public_service_career_and_slot_collections_are_successful(self):
        for path in (
            "/api/services/public/services/",
            "/api/services/public/main-services/",
            "/api/services/public/careers/jobs/",
            "/api/services/public/appointments/slots/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_missing_dynamic_form_and_access_link_return_not_found(self):
        form = self.client.get("/api/public/forms/missing-form/")
        snapshot = self.client.get("/api/services/public/request-access/missing-key/")
        otp = self.client.post(
            "/api/services/public/request-access/send-otp/",
            {"public_key": "missing-key"},
            format="json",
        )

        self.assertEqual(form.status_code, 404)
        self.assertEqual(snapshot.status_code, 404)
        self.assertEqual(otp.status_code, 404)

    def test_invalid_otp_payload_returns_bad_request(self):
        response = self.client.post(
            "/api/services/public/request-access/verify-otp/", {}, format="json"
        )

        self.assertEqual(response.status_code, 400)
