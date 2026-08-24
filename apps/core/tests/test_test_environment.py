from django.conf import settings
from django.test import SimpleTestCase


class TestEnvironmentContractTests(SimpleTestCase):
    def test_manage_test_command_uses_isolated_sqlite_database(self):
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.sqlite3",
        )
        self.assertNotEqual(str(settings.DATABASES["default"]["NAME"]), "db.sqlite3")
