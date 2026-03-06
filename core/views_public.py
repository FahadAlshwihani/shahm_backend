from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.utils.text import slugify

# Settings
from settings_app.models import SiteSettings
from settings_app.serializers import SiteSettingsSerializer

# CMS
from cms.models import HeroSection, FooterColumn, Page, HeaderLink
from cms.serializers import (
    HeroSectionSerializer,
    FooterColumnSerializer,
    PageSerializer,
    HeaderLinkSerializer,
)
from cms.views import PublicHomeView

# Services
from services.models import PracticeArea, Service
from services.serializers import PracticeAreaSerializer

# Blog
from blog.models import BlogPost
from blog.serializers_public import PublicBlogPostSerializer

# Team
from team.models import TeamMember
from team.serializers import TeamMemberSerializer

# Legal
from legal.models import LegalPage
from legal.serializers import LegalPageSerializer

# SEO
from seo.models import DefaultSEO, PageSEO
from seo.serializers import DefaultSEOSerializer, PageSEOSerializer

# Messaging
from messaging.models import ContactMessage, Subscriber

# Visits
from core.models import Visit

# Permissions
from core.permissions import IsAdminOrSuper



# ---------------------------------------------------------
# 1) Site Settings
# ---------------------------------------------------------
class PublicSiteSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = SiteSettings.objects.first()
        return Response(SiteSettingsSerializer(settings).data)



# ---------------------------------------------------------
# 2) Hero (single hero by slug)
# ---------------------------------------------------------
class PublicHeroView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            hero = HeroSection.objects.get(slug=slug, is_active=True)
        except HeroSection.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        return Response(HeroSectionSerializer(hero, context={"request": request}).data)



# ---------------------------------------------------------
# 3) Footer
# ---------------------------------------------------------
class PublicFooterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cols = FooterColumn.objects.filter(is_active=True).order_by("order")

        data = FooterColumnSerializer(
            cols,
            many=True,
            context={"request": request}
        ).data

        col_dict = {c["title_ar"]: c for c in data}

        # =====================================================
        # Sitemap — ALL CMS Pages (same shape as FooterLink)
        # =====================================================
        if "خريطة الموقع" in col_dict:
            pages = Page.objects.filter(
                is_published=True,
                show_in_sitemap=True
            ).order_by("slug")

            col_dict["خريطة الموقع"]["links"] = [
                {
                    "id": f"page-{p.id}",
                    "label_ar": p.title_ar,
                    "label_en": p.title_en,
                    "resolved_url": f"/page/{p.slug}",
                    "children": [],
                    "is_active": True,
                }
                for p in pages
            ]

        # =====================================================
        # Socials + Footer Logo (كما هو)
        # =====================================================
        settings = SiteSettings.objects.first()
        socials = []

        if settings:
            mapping = [
                ("WhatsApp", settings.whatsapp_number, "https://wa.me/"),
                ("LinkedIn", settings.linkedin_url, ""),
                ("X", settings.x_url, ""),
                ("Instagram", settings.instagram_url, ""),
            ]

            for label, value, prefix in mapping:
                if value:
                    socials.append({
                        "label_ar": label,
                        "label_en": label,
                        "url": prefix + value if prefix else value,
                        "children": [],
                        "is_active": True,
                    })

        if "تابعنا" in col_dict:
            existing = col_dict["تابعنا"].get("links", [])
            logo = next(
                (l for l in existing if l.get("media_type") == "footer_logo"),
                None
            )
            col_dict["تابعنا"]["links"] = ([logo] if logo else []) + socials

        # =====================================================
        # Newsletter
        # =====================================================
        if "أرغب في تلقّي كل جديد من أخبار شهم" in col_dict:
            col_dict["أرغب في تلقّي كل جديد من أخبار شهم"]["links"] = []


        # =======================
        # Final response
        # =======================
        return Response(
            sorted(col_dict.values(), key=lambda x: x["order"])
        )

# ---------------------------------------------------------
# 4) Dynamic CMS Page
# ---------------------------------------------------------
class PublicPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            page = Page.objects.get(slug=slug, is_published=True)
        except Page.DoesNotExist:
            return Response({"detail": "Page not found"}, status=404)

        try:
            seo = PageSEO.objects.get(slug=slug)
        except PageSEO.DoesNotExist:
            seo = DefaultSEO.objects.first()

        return Response({
            "seo": PageSEOSerializer(seo).data if seo else None,
            "page": PageSerializer(page, context={"request": request}).data,
        })



# ---------------------------------------------------------
# 5) Legal Pages
# ---------------------------------------------------------
class PublicLegalPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            page = LegalPage.objects.get(slug=slug, is_published=True)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        try:
            seo = PageSEO.objects.get(slug=slug)
        except PageSEO.DoesNotExist:
            seo = DefaultSEO.objects.first()

        return Response({
            "seo": PageSEOSerializer(seo).data if seo else None,
            "page": LegalPageSerializer(page, context={"request": request}).data,
        })



# ---------------------------------------------------------
# 6) Services
# ---------------------------------------------------------
class PublicPracticeAreasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        areas = PracticeArea.objects.filter(is_active=True).order_by("order")
        return Response(PracticeAreaSerializer(areas, many=True, context={"request": request}).data)


class PublicPracticeAreaDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            area = PracticeArea.objects.get(slug=slug, is_active=True)
        except PracticeArea.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)
        return Response(PracticeAreaSerializer(area, context={"request": request}).data)


# ---------------------------------------------------------
# 7) BLOG — PUBLIC (FINAL & CORRECT)
# ---------------------------------------------------------
class PublicBlogListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        posts = (
            BlogPost.objects
            .filter(status="published")
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        return Response(
            PublicBlogPostSerializer(
                posts,
                many=True,
                context={"request": request}
            ).data
        )


class PublicBlogDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            post = (
                BlogPost.objects
                .select_related("category")
                .prefetch_related("tags")
                .get(slug=slug, status="published")
            )
        except BlogPost.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)

        post.views_count = (post.views_count or 0) + 1
        post.save(update_fields=["views_count"])

        return Response(
            PublicBlogPostSerializer(
                post,
                context={"request": request}
            ).data
        )



# ---------------------------------------------------------
# 8) Team
# ---------------------------------------------------------
class PublicTeamView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        team = TeamMember.objects.filter(is_active=True).order_by("order")
        return Response(TeamMemberSerializer(team, many=True).data)



# ---------------------------------------------------------
# 9) SEO
# ---------------------------------------------------------
class PublicSEOView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug=None):

        if slug:
            try:
                seo = PageSEO.objects.get(slug=slug)
                return Response(PageSEOSerializer(seo).data)
            except PageSEO.DoesNotExist:
                pass

        default = DefaultSEO.objects.first()
        return Response(DefaultSEOSerializer(default).data if default else {})



# ---------------------------------------------------------
# 10) Header Menu
# ---------------------------------------------------------
class PublicHeaderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        roots = HeaderLink.objects.filter(
            parent__isnull=True, is_active=True
        ).order_by("order")

        ser = HeaderLinkSerializer(
            roots,
            many=True,
            context={"request": request}
        )
        return Response(ser.data)



# ---------------------------------------------------------
# 11) Dashboard Stats
# ---------------------------------------------------------
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

    def get(self, request):

        now = timezone.now()
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_visits = Visit.objects.count()
        today_visits = Visit.objects.filter(visited_at__gte=start_today).count()
        week_visits = Visit.objects.filter(visited_at__gte=now - timedelta(days=7)).count()
        month_visits = Visit.objects.filter(visited_at__gte=now - timedelta(days=30)).count()

        latest_visits = Visit.objects.order_by("-visited_at")[:20]

        top_pages = (
            Visit.objects.values("path")
            .annotate(count=models.Count("path"))
            .order_by("-count")[:10]
        )

        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        latest_messages = ContactMessage.objects.order_by("-created_at")[:5]

        total_subscribers = Subscriber.objects.count()
        latest_subscribers = Subscriber.objects.order_by("-created_at")[:5]

        published_posts = BlogPost.objects.filter(status="published").count()
        total_practice = PracticeArea.objects.count()
        total_services = Service.objects.count()

        return Response({
            "visits": {
                "total": total_visits,
                "today": today_visits,
                "week": week_visits,
                "month": month_visits,
                "latest": [
                    {
                        "ip": v.ip_address,
                        "path": v.path,
                        "ua": v.user_agent,
                        "time": v.visited_at,
                    }
                    for v in latest_visits
                ],
                "top_pages": list(top_pages),
            },
            "messages": {
                "total": total_messages,
                "unread": unread_messages,
                "latest": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "email": m.email,
                        "subject": m.subject,
                        "created_at": m.created_at,
                    }
                    for m in latest_messages
                ],
            },
            "subscribers": {
                "total": total_subscribers,
                "latest": [
                    {
                        "id": s.id,
                        "email": s.email,
                        "created_at": s.created_at,
                    }
                    for s in latest_subscribers
                ],
            },
            "blog": {
                "published_posts": published_posts,
            },
            "services": {
                "practice_areas": total_practice,
                "services": total_services,
            }
        })
