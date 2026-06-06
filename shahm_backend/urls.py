from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from django.conf import settings
from django.conf.urls.static import static


def robots_txt(request):
    content = "User-agent: *\nDisallow:\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    urls = [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/services",
        "https://example.com/contact",
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for u in urls:
        xml += f"  <url><loc>{u}</loc></url>\n"

    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")


urlpatterns = [
    path("admin/", admin.site.urls),

    # ---------------------------
    # Public API
    # ---------------------------
    path("api/public/", include("core.urls_public")),

    # ---------------------------
    # Dashboard APIs
    # ---------------------------
    path("api/settings/", include("settings_app.urls")),
    path("api/messaging/", include("messaging.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/cms/", include("cms.urls")),
    path("api/legal/", include("legal.urls")),
    path("api/blog/", include("blog.urls")),
    path("api/team/", include("team.urls")),
    path("api/services/", include("services.urls")),
    path("api/seo/", include("seo.urls")),
    path("api/", include("form_builder.urls")),

    # ---------------------------
    # System files
    # ---------------------------
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
]

# ---------------------------
# MEDIA FILES (Uploads)
# ---------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
