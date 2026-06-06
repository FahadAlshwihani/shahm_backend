from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.db.models import Q, Prefetch
from cms.models import Page as CMSPage
from blog.models import BlogPost
from services.models import Service

from accounts.permissions import IsEditorOrAbove

from .models import (
    HeroSection,
    HeroMedia,
    FooterColumn,
    FooterLink,
    Page,
    HomeSection,
    HeaderLink,
    FAQItem,
    ContactFAQPreview,
    ContactCard,
    ContactPageSettings,
    PageContent,
    FooterSettings,
    FooterCTA,
    FAQCategory,
    AboutPage,
    AboutStat,
    AboutPost,
    AboutSection,
    AboutIcon,
    AboutPartner,
)

from .serializers import (
    HeroSectionSerializer,
    HeroMediaSerializer,
    FooterColumnSerializer,
    FooterLinkSerializer,
    PageSerializer,
    HomeSectionSerializer,
    PublicHomeSectionSerializer,
    HeaderLinkSerializer,
    FAQItemSerializer,
    ContactFAQPreviewSerializer,
    ContactCardSerializer,
    ContactPageSettingsSerializer,
    PageContentSerializer,
    FooterSettingsSerializer,
    FooterCTASerializer,
    FAQCategorySerializer,
    AboutPageSerializer,
    AboutStatSerializer,
    AboutPostSerializer,
    AboutSectionSerializer,
    AboutIconSerializer,
    AboutPartnerSerializer,
)


# ============================================================
# PUBLIC
# ============================================================

class PublicHeroView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        hero = get_object_or_404(HeroSection, slug=slug, is_active=True)
        ser = HeroSectionSerializer(hero, context={"request": request})
        return Response(ser.data)


class PublicPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug, is_published=True)
        return Response(PageSerializer(page).data)


class PublicHeaderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = HeaderLink.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related(
            Prefetch(
                "children",
                queryset=HeaderLink.objects.filter(is_active=True).order_by("order")
            ),
            Prefetch(
                "children__children",
                queryset=HeaderLink.objects.filter(is_active=True).order_by("order")
            )
        ).order_by("order")

        serializer = HeaderLinkSerializer(
            items,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class PublicHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        hero_obj = HeroSection.objects.filter(is_active=True).order_by("order").first()

        hero_data = (
            HeroSectionSerializer(hero_obj, context={"request": request}).data
            if hero_obj else None
        )

        footer_columns = FooterColumn.objects.filter(
            is_active=True
        ).prefetch_related(
            "links",
            "links__children"
        ).select_related()

        footer_settings = FooterSettings.objects.first()

        footer_cta = FooterCTA.objects.filter(
            is_active=True
        ).order_by("order")

        footer_payload = {

            "columns": FooterColumnSerializer(
                footer_columns,
                many=True,
                context={"request": request}
            ).data,

            "cta_buttons": FooterCTASerializer(
                footer_cta,
                many=True
            ).data,

            "settings": FooterSettingsSerializer(
                footer_settings,
                context={"request": request}
            ).data if footer_settings else None

        }

        sections = HomeSection.objects.filter(is_active=True).order_by("order")
        sec_ser = PublicHomeSectionSerializer(sections, many=True).data

        return Response({

            "hero": hero_data,

            "sections": sec_ser,

            "footer": footer_payload,

        })


# ============================================================
# ADMIN — HERO CRUD
# ============================================================

class HeroListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        heroes = HeroSection.objects.all().order_by("order")
        ser = HeroSectionSerializer(heroes, many=True, context={"request": request})
        return Response(ser.data)

    def post(self, request):
        ser = HeroSectionSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


class HeroDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        hero = get_object_or_404(HeroSection, pk=pk)
        return Response(HeroSectionSerializer(hero).data)

    def patch(self, request, pk):
        hero = get_object_or_404(HeroSection, pk=pk)
        ser = HeroSectionSerializer(hero, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        hero = get_object_or_404(HeroSection, pk=pk)
        hero.delete()
        return Response(status=204)


# ============================================================
# ADMIN — HERO MEDIA CRUD
# ============================================================

class HeroMediaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, hero_id):
        hero = get_object_or_404(HeroSection, pk=hero_id)
        media = HeroMedia.objects.filter(hero=hero).order_by("order")
        return Response(
            HeroMediaSerializer(
                media,
                many=True,
                context={"request": request}
            ).data
        )

    def post(self, request, hero_id):
        hero = get_object_or_404(HeroSection, pk=hero_id)

        ser = HeroMediaSerializer(
            data=request.data,
            context={"request": request}
        )

        if ser.is_valid():
            ser.save(hero=hero)
            return Response(ser.data, status=201)

        return Response(ser.errors, status=400)


class HeroMediaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        media = get_object_or_404(HeroMedia, pk=pk)
        ser = HeroMediaSerializer(media, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        media = get_object_or_404(HeroMedia, pk=pk)
        media.delete()
        return Response(status=204)


# ============================================================
# ADMIN — Pages CRUD (WITH AUTO-ADD & AUTO-UPDATE)
# ============================================================

class PageListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        pages = Page.objects.all().order_by("slug")
        return Response(PageSerializer(pages, many=True).data)

    def post(self, request):
        ser = PageSerializer(data=request.data)

        if ser.is_valid():
            page = ser.save()

            return Response(PageSerializer(page).data, status=201)

        return Response(ser.errors, status=400)


class PageDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return Response(PageSerializer(page).data)

    def patch(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        old_slug = page.slug  # needed to detect changes

        ser = PageSerializer(page, data=request.data, partial=True)

        if ser.is_valid():
            page = ser.save()

            return Response(PageSerializer(page).data)

        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        page = get_object_or_404(Page, pk=pk)

        page.delete()
        return Response(status=204)


# ============================================================
# ADMIN — Home Sections
# ============================================================

class HomeSectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        secs = HomeSection.objects.all().order_by("order")
        return Response(HomeSectionSerializer(secs, many=True).data)

    def post(self, request):
        ser = HomeSectionSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


class HomeSectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        sec = get_object_or_404(HomeSection, pk=pk)
        ser = HomeSectionSerializer(sec, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        sec = get_object_or_404(HomeSection, pk=pk)
        sec.delete()
        return Response(status=204)


# ============================================================
# ADMIN — Header CRUD
# ============================================================

class HeaderLinkListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        links = HeaderLink.objects.all().order_by("order")
        serializer = HeaderLinkSerializer(
            links,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        if request.data.get("type") == "logo":
            HeaderLink.objects.filter(
                type="logo",
                logo_variant=request.data.get("logo_variant"),
            ).delete()

        serializer = HeaderLinkSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        response_serializer = HeaderLinkSerializer(
            obj,
            context={"request": request},
        )
        return Response(response_serializer.data, status=201)


class HeaderLinkDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def patch(self, request, pk):
        link = get_object_or_404(HeaderLink, pk=pk)
        serializer = HeaderLinkSerializer(
            link,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        response_serializer = HeaderLinkSerializer(
            obj,
            context={"request": request},
        )
        return Response(response_serializer.data)

    def delete(self, request, pk):
        link = get_object_or_404(HeaderLink, pk=pk)
        link.delete()
        return Response(status=204)


# ============================================================
# ADMIN — Footer CRUD
# ============================================================

class FooterColumnListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        cols = FooterColumn.objects.all().order_by("order")
        return Response(FooterColumnSerializer(cols, many=True).data)

    def post(self, request):
        ser = FooterColumnSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


class FooterColumnDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        col = get_object_or_404(FooterColumn, pk=pk)
        ser = FooterColumnSerializer(col, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        col = get_object_or_404(FooterColumn, pk=pk)
        col.delete()
        return Response(status=204)


class FooterLinkListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        if request.data.get("url") and request.data.get("page"):
            return Response(
                {"detail": "لا يمكن استخدام URL + صفحة CMS معًا"},
                status=400
            )

        # ✅ منع أكثر من شعار
        if request.data.get("media_type") == "footer_logo":
            FooterLink.objects.filter(
                column_id=request.data.get("column"),
                media_type="footer_logo"
            ).delete()

        ser = FooterLinkSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)

        return Response(ser.errors, status=400)


class FooterLinkDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        link = get_object_or_404(FooterLink, pk=pk)

        if request.data.get("url") and request.data.get("page"):
            return Response({"detail": "لا يمكن استخدام URL + صفحة CMS معًا"}, status=400)

        ser = FooterLinkSerializer(link, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        link = get_object_or_404(FooterLink, pk=pk)
        link.delete()
        return Response(status=204)

    # ================= Search =================


def public_search(request):
    q = request.GET.get("q", "").strip()
    lang = request.GET.get("lang", "ar")

    if len(q) < 2:
        return JsonResponse([], safe=False)

    results = []

    # ================= Pages =================
    pages = CMSPage.objects.filter(
        Q(title_ar__icontains=q) |
        Q(title_en__icontains=q),
        is_published=True,
        show_in_sitemap=True
    )[:5]

    for p in pages:
        results.append({
            "type": "page",
            "title": p.title_ar if lang == "ar" else p.title_en,
            "url": f"/page/{p.slug}"
        })

    # ================= Blog =================
    blogs = BlogPost.objects.filter(
        Q(title_ar__icontains=q) |
        Q(title_en__icontains=q),
        status="published"
    )[:5]

    for b in blogs:
        results.append({
            "type": "blog",
            "title": b.title_ar if lang == "ar" else b.title_en,
            "url": f"/blog/{b.slug}"
        })

    # ================= Services =================
    services = Service.objects.filter(
        Q(title_ar__icontains=q) |
        Q(title_en__icontains=q),
        is_active=True
    )[:5]

    for s in services:
        results.append({
            "type": "service",
            "title": s.title_ar if lang == "ar" else s.title_en,
            "url": f"/services/{s.slug}"
        })

    # ترتيب النتائج (اختياري)
    results = sorted(results, key=lambda x: x["type"])

    return JsonResponse(results[:10], safe=False)


# ================== PUBLIC FAQ ==================

class PublicFAQView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category_slug = request.GET.get("category")

        categories = FAQCategory.objects.filter(is_active=True)

        if category_slug:
            categories = categories.filter(slug=category_slug)

        categories = categories.prefetch_related(
            Prefetch(
                "faqs",
                queryset=FAQItem.objects.filter(is_active=True).order_by("order")
            )
        ).order_by("order")

        ser = FAQCategorySerializer(categories, many=True, context={"request": request})
        return Response(ser.data)


# ================== ADMIN FAQ ==================

class FAQCategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        items = FAQCategory.objects.all().order_by("order")
        return Response(FAQCategorySerializer(items, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = FAQCategorySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class FAQCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        obj = get_object_or_404(FAQCategory, pk=pk)
        serializer = FAQCategorySerializer(obj, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = get_object_or_404(FAQCategory, pk=pk)
        obj.delete()
        return Response(status=204)


class FAQListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        items = FAQItem.objects.all().order_by("order")
        return Response(FAQItemSerializer(items, many=True).data)

    def post(self, request):
        ser = FAQItemSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


class FAQDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        item = get_object_or_404(FAQItem, pk=pk)
        ser = FAQItemSerializer(item, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)

    def delete(self, request, pk):
        item = get_object_or_404(FAQItem, pk=pk)
        item.delete()
        return Response(status=204)


# ================== ADMIN CONTACT PAGE ==================

class ContactFAQPreviewView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        all_faqs = FAQItem.objects.filter(is_active=True).order_by("order")

        selected = ContactFAQPreview.objects.filter(is_active=True)
        selected_ids = selected.values_list("faq_id", flat=True)

        return Response({
            "all_faqs": FAQItemSerializer(all_faqs, many=True).data,
            "selected_ids": list(selected_ids),
        })

    def post(self, request):
        ser = ContactFAQPreviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class ContactFAQPreviewToggleView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request):
        faq_id = request.data.get("faq_id")

        if not faq_id:
            return Response(
                {"detail": "faq_id is required"},
                status=400
            )

        # إذا موجود → نحذفه (إلغاء)
        existing = ContactFAQPreview.objects.filter(faq_id=faq_id).first()

        if existing:
            existing.delete()
            return Response({"status": "removed"})

        # إذا غير موجود → نضيفه
        ContactFAQPreview.objects.create(faq_id=faq_id)
        return Response({"status": "added"})


# ================== CONTACT CARDS ==================

class ContactCardListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        cards = ContactCard.objects.all().order_by("order")
        return Response(ContactCardSerializer(cards, many=True).data)

    def post(self, request):
        ser = ContactCardSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=201)


class ContactCardDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        card = get_object_or_404(ContactCard, pk=pk)
        ser = ContactCardSerializer(card, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def delete(self, request, pk):
        get_object_or_404(ContactCard, pk=pk).delete()
        return Response(status=204)


class PublicContactPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = ContactPageSettings.objects.first()

        cards = (
            ContactCard.objects
            .filter(is_active=True)
            .select_related(
                "primary_form",
                "secondary_form",
                "primary_info_modal",
                "secondary_info_modal",
            )
            .prefetch_related(
                "primary_info_modal__sections",
                "secondary_info_modal__sections",
            )
            .order_by("order")
        )
        faq_preview = ContactFAQPreview.objects.filter(is_active=True)

        return Response({
            "title_ar": settings.title_ar if settings else "",
            "title_en": settings.title_en if settings else "",
            "description_ar": settings.description_ar if settings else "",
            "description_en": settings.description_en if settings else "",

            "cards": ContactCardSerializer(cards, many=True).data,
            "faq_preview": ContactFAQPreviewSerializer(faq_preview, many=True).data,
        })


class ContactPageSettingsAdminView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        obj, _ = ContactPageSettings.objects.get_or_create(id=1)
        return Response(ContactPageSettingsSerializer(obj).data)

    def post(self, request):
        obj, _ = ContactPageSettings.objects.get_or_create(id=1)
        ser = ContactPageSettingsSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class PublicPageContentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        page = get_object_or_404(PageContent, slug=slug)
        return Response(PageContentSerializer(page).data)


class AdminPageContentView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, slug):
        page = get_object_or_404(PageContent, slug=slug)
        serializer = PageContentSerializer(page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FooterSettingsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        obj, _ = FooterSettings.objects.get_or_create(id=1)

        return Response(

            FooterSettingsSerializer(
                obj,
                context={"request": request}
            ).data
        )

    def post(self, request):
        obj, _ = FooterSettings.objects.get_or_create(id=1)

        serializer = FooterSettingsSerializer(

            obj,

            data=request.data,

            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class FooterCTAListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        items = FooterCTA.objects.all()

        return Response(

            FooterCTASerializer(items, many=True).data
        )

    def post(self, request):
        serializer = FooterCTASerializer(

            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=201)


class FooterCTADetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        obj = get_object_or_404(FooterCTA, pk=pk)

        serializer = FooterCTASerializer(

            obj,

            data=request.data,

            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        obj = get_object_or_404(FooterCTA, pk=pk)

        obj.delete()

        return Response(status=204)


# views.py
class PublicFooterSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        obj = FooterSettings.objects.first()

        return Response(
            FooterSettingsSerializer(
                obj,
                context={"request": request}
            ).data
        )


class PublicAboutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = AboutPage.objects.filter(is_active=True).prefetch_related(
            "stats",
            "posts",
            "sections__icons",
            "partners"
        ).first()

        if not page:
            return Response({})

        return Response(AboutPageSerializer(page, context={"request": request}).data)


class AdminAboutView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def get(self, request):
        obj, _ = AboutPage.objects.get_or_create(id=1)

        return Response(
            AboutPageSerializer(
                obj,
                context={"request": request}
            ).data
        )

    def patch(self, request):
        obj, _ = AboutPage.objects.get_or_create(id=1)

        serializer = AboutPageSerializer(
            obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# ============================================================
# ADMIN — ABOUT PAGE CRUD
# ============================================================

def get_about_page():
    obj, _ = AboutPage.objects.get_or_create(id=1)
    return obj


class AdminAboutStatListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request):
        page = get_about_page()
        serializer = AboutStatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page)
        return Response(serializer.data, status=201)


class AdminAboutStatDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        obj = get_object_or_404(AboutStat, pk=pk)
        serializer = AboutStatSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        get_object_or_404(AboutStat, pk=pk).delete()
        return Response(status=204)


class AdminAboutPostListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        page = get_about_page()
        serializer = AboutPostSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page)
        return Response(serializer.data, status=201)


class AdminAboutPostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        obj = get_object_or_404(AboutPost, pk=pk)
        serializer = AboutPostSerializer(
            obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        get_object_or_404(AboutPost, pk=pk).delete()
        return Response(status=204)


class AdminAboutSectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request):
        page = get_about_page()
        serializer = AboutSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page)
        return Response(serializer.data, status=201)


class AdminAboutSectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        obj = get_object_or_404(AboutSection, pk=pk)
        serializer = AboutSectionSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        get_object_or_404(AboutSection, pk=pk).delete()
        return Response(status=204)


class AdminAboutIconListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AboutIconSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class AdminAboutIconDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        obj = get_object_or_404(AboutIcon, pk=pk)
        serializer = AboutIconSerializer(
            obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        get_object_or_404(AboutIcon, pk=pk).delete()
        return Response(status=204)


class AdminAboutPartnerListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        page = get_about_page()
        serializer = AboutPartnerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page)
        return Response(serializer.data, status=201)


class AdminAboutPartnerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        obj = get_object_or_404(AboutPartner, pk=pk)
        serializer = AboutPartnerSerializer(
            obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        get_object_or_404(AboutPartner, pk=pk).delete()
        return Response(status=204)
