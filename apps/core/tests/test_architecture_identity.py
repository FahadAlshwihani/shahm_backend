from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase


class ArchitectureIdentityTests(SimpleTestCase):
    expected_apps = {
        "accounts",
        "blog",
        "cms",
        "core",
        "form_builder",
        "legal",
        "messaging",
        "seo",
        "services",
        "settings_app",
        "team",
    }

    def test_domain_app_names_and_labels_remain_stable(self):
        identities = {
            config.label: config.name
            for config in apps.get_app_configs()
            if config.label in self.expected_apps
        }

        self.assertEqual(
            identities,
            {
                app_name: f"apps.{app_name}"
                for app_name in self.expected_apps
            },
        )

    def test_representative_database_tables_remain_stable(self):
        expected_tables = {
            "accounts.User": "accounts_user",
            "core.Visit": "core_visit",
            "cms.ContactCard": "cms_contactcard",
            "services.Service": "services_service",
            "form_builder.FormTemplate": "form_builder_formtemplate",
        }

        for model_label, table_name in expected_tables.items():
            with self.subTest(model=model_label):
                self.assertEqual(
                    apps.get_model(model_label)._meta.db_table,
                    table_name,
                )

    def test_public_url_and_wsgi_settings_keep_expected_contracts(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertEqual(settings.ROOT_URLCONF, "config.urls")
        self.assertEqual(settings.WSGI_APPLICATION, "config.wsgi.application")

    def test_canonical_project_imports_are_available(self):
        from config.urls import sitemap_xml as canonical_sitemap
        from config.wsgi import application as canonical_wsgi

        self.assertTrue(callable(canonical_sitemap))
        self.assertIsNotNone(canonical_wsgi)
