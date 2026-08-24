"""Root URL configuration grouped by application domain."""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from django.conf import settings
from django.conf.urls.static import static


def robots_txt(request):
    content = "User-agent: *\nDisallow:\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    site_url = settings.SITE_URL.rstrip("/")
    urls = [
        f"{site_url}/",
        f"{site_url}/about",
        f"{site_url}/services",
        f"{site_url}/contact",
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for u in urls:
        xml += f"  <url><loc>{u}</loc></url>\n"

    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")


urlpatterns = [
    # Django administration
    path("admin/", admin.site.urls),

    # =========================================================
    # PUBLIC CORE API
    # =========================================================
    path("api/public/", include("apps.core.urls_public")),

    # =========================================================
    # AUTHENTICATION AND USERS
    # =========================================================
    path("api/accounts/", include("apps.accounts.urls")),

    # =========================================================
    # SETTINGS AND MESSAGING
    # =========================================================
    path("api/settings/", include("apps.settings_app.urls")),
    path("api/messaging/", include("apps.messaging.urls")),

    # =========================================================
    # CONTENT MANAGEMENT
    # =========================================================
    path("api/cms/", include("apps.cms.urls")),
    path("api/legal/", include("apps.legal.urls")),
    path("api/blog/", include("apps.blog.urls")),
    path("api/team/", include("apps.team.urls")),
    path("api/seo/", include("apps.seo.urls")),

    # =========================================================
    # SERVICES AND DYNAMIC FORMS
    # =========================================================
    path("api/services/", include("apps.services.urls")),
    path("api/", include("apps.form_builder.urls")),

    # =========================================================
    # SYSTEM FILES
    # =========================================================
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
]

# ---------------------------
# MEDIA FILES (Uploads)
# ---------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
