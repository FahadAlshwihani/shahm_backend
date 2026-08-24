# seo/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.accounts.permissions import IsAdminOrSuper

from .models import DefaultSEO, PageSEO
from .serializers import DefaultSEOSerializer, PageSEOSerializer

from apps.cms.models import Page
from apps.legal.models import LegalPage
from apps.services.models import PracticeArea
from apps.blog.models import BlogPost
from apps.team.models import TeamMember


# -----------------------------------------------------
# PUBLIC SEO (يستخدم في الموقع العام + fallback)
# -----------------------------------------------------
class PublicSEOView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug=None):
        """
        - لو فيه slug → نحاول نرجع PageSEO مخصص
        - لو ما فيه أو ما لقيناه → نرجع DefaultSEO
        - ما نرجّع 404 أبدًا هنا عشان الفرونت ما يطيح
        """

        # 1) لو فيه SEO مخصص للصفحة
        if slug:
            seo = PageSEO.objects.filter(slug=slug).first()
            if seo:
                return Response(PageSEOSerializer(seo).data)

        # 2) لو مافيه SEO مخصص → نضمن وجود DefaultSEO
        default, created = DefaultSEO.objects.get_or_create(
            pk=1,  # نخلي record واحد ثابت
            defaults={
                "site_title": "",
                "site_description": "",
                "keywords": "",
                "og_title": "",
                "og_description": "",
                "twitter_title": "",
                "twitter_description": "",
                "canonical_base": "",
            },
        )

        return Response(DefaultSEOSerializer(default).data)


# -----------------------------------------------------
# ADMIN: DEFAULT SEO
# -----------------------------------------------------
class DefaultSEOView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

    def get(self, request):
        """
        نضمن دومًا وجود DefaultSEO ونرجّعه
        """
        default, created = DefaultSEO.objects.get_or_create(
            pk=1,
            defaults={
                "site_title": "",
                "site_description": "",
                "keywords": "",
                "og_title": "",
                "og_description": "",
                "twitter_title": "",
                "twitter_description": "",
                "canonical_base": "",
            },
        )
        return Response(DefaultSEOSerializer(default).data)

    def put(self, request):
        """
        تحديث DefaultSEO (يُنشأ لو مافيه)
        """
        default, created = DefaultSEO.objects.get_or_create(pk=1)
        serializer = DefaultSEOSerializer(default, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# -----------------------------------------------------
# ADMIN: PAGE SEO CRUD
# -----------------------------------------------------
class PageSEOListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

    def get(self, request):
        seo_items = PageSEO.objects.all()
        return Response(PageSEOSerializer(seo_items, many=True).data)

    def post(self, request):
        serializer = PageSEOSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PageSEODetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

    def get_object(self, pk):
        try:
            return PageSEO.objects.get(id=pk)
        except PageSEO.DoesNotExist:
            return None

    def get(self, request, pk):
        seo = self.get_object(pk)
        if not seo:
            return Response({"detail": "Not found"}, status=404)
        return Response(PageSEOSerializer(seo).data)

    def patch(self, request, pk):
        seo = self.get_object(pk)
        if not seo:
            return Response({"detail": "Not found"}, status=404)

        serializer = PageSEOSerializer(seo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        seo = self.get_object(pk)
        if not seo:
            return Response({"detail": "Not found"}, status=404)

        seo.delete()
        return Response(status=204)


# -----------------------------------------------------
# ADMIN: Return ALL pages for SEO selection
# -----------------------------------------------------
class AllPagesForSEO(APIView):
    """
    ترجع قائمة بكل الصفحات/الخدمات/المدونة/الفريق
    على شكل items:
    {
        "type": "cms" | "legal" | "service" | "blog" | "team",
        "title": "...",
        "slug": "...",
        "has_seo": true/false,
    }

    الكود هنا "متحصّن" try/except لكل بلوك
    عشان أي اختلاف بسيط في الموديل ما يسبب 500.
    """
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

    def get(self, request):
        pages = []

        # ========== CMS PAGES ==========
        try:
            cms_qs = Page.objects.all()
            if hasattr(Page, "is_published"):
                cms_qs = cms_qs.filter(is_published=True)

            for p in cms_qs:
                title = getattr(p, "title_ar", None) or getattr(p, "title_en", None) or str(p)
                slug = getattr(p, "slug", None) or str(p.pk)
                if not slug:
                    continue

                pages.append({
                    "type": "cms",
                    "title": title,
                    "slug": slug,
                    "has_seo": PageSEO.objects.filter(slug=slug).exists(),
                })
        except Exception:
            pass

        # ========== LEGAL PAGES ==========
        try:
            legal_qs = LegalPage.objects.all()
            if hasattr(LegalPage, "is_published"):
                legal_qs = legal_qs.filter(is_published=True)

            for p in legal_qs:
                title = getattr(p, "title_ar", None) or getattr(p, "title_en", None) or str(p)
                slug = getattr(p, "slug", None) or str(p.pk)
                if not slug:
                    continue

                pages.append({
                    "type": "legal",
                    "title": title,
                    "slug": slug,
                    "has_seo": PageSEO.objects.filter(slug=slug).exists(),
                })
        except Exception:
            pass

        # ========== SERVICES ==========
        try:
            service_qs = PracticeArea.objects.all()
            if hasattr(PracticeArea, "is_active"):
                service_qs = service_qs.filter(is_active=True)

            for s in service_qs:
                title = (
                    getattr(s, "title_ar", None)
                    or getattr(s, "name_ar", None)
                    or getattr(s, "title_en", None)
                    or getattr(s, "name_en", None)
                    or str(s)
                )
                slug = getattr(s, "slug", None) or str(s.pk)
                if not slug:
                    continue

                pages.append({
                    "type": "service",
                    "title": title,
                    "slug": slug,
                    "has_seo": PageSEO.objects.filter(slug=slug).exists(),
                })
        except Exception:
            pass

        # ========== BLOG POSTS ==========
        try:
            blog_qs = BlogPost.objects.all()
            # لو فيه حقل status نفلتر على published، غير كذا نجيب الكل
            if hasattr(BlogPost, "status"):
                try:
                    blog_qs = blog_qs.filter(status="published")
                except Exception:
                    # لو الاسم مختلف أو choices مختلفة، نطنش الفلتر
                    pass

            for b in blog_qs:
                title = (
                    getattr(b, "title_ar", None)
                    or getattr(b, "title_en", None)
                    or getattr(b, "title", None)
                    or str(b)
                )
                slug = getattr(b, "slug", None) or str(b.pk)
                if not slug:
                    continue

                pages.append({
                    "type": "blog",
                    "title": title,
                    "slug": slug,
                    "has_seo": PageSEO.objects.filter(slug=slug).exists(),
                })
        except Exception:
            pass

        # ========== TEAM MEMBERS ==========
        try:
            team_qs = TeamMember.objects.all()
            if hasattr(TeamMember, "is_active"):
                team_qs = team_qs.filter(is_active=True)

            for t in team_qs:
                title = (
                    getattr(t, "full_name_ar", None)
                    or getattr(t, "full_name_en", None)
                    or getattr(t, "name_ar", None)
                    or getattr(t, "name_en", None)
                    or str(t)
                )
                slug = f"team-{t.pk}"

                pages.append({
                    "type": "team",
                    "title": title,
                    "slug": slug,
                    "has_seo": PageSEO.objects.filter(slug=slug).exists(),
                })
        except Exception:
            pass

        return Response(pages)
