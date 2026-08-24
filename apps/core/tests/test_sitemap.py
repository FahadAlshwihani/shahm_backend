from django.test import RequestFactory, SimpleTestCase, override_settings

from config.urls import sitemap_xml


class SitemapTests(SimpleTestCase):
    @override_settings(SITE_URL="https://shahmlaw.sa")
    def test_sitemap_uses_configured_canonical_domain(self):
        response = sitemap_xml(RequestFactory().get("/sitemap.xml"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("https://shahmlaw.sa/about", content)
        self.assertNotIn("example.com", content)
