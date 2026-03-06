from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.db.models import Q
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

)

from accounts.permissions import IsEditorOrAbove


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
        roots = HeaderLink.objects.filter(
            parent__isnull=True, is_active=True
        ).order_by("order")

        ser = HeaderLinkSerializer(roots, many=True)
        return Response(ser.data)


class PublicHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        hero_obj = HeroSection.objects.filter(is_active=True).order_by("order").first()

        hero_data = (
            HeroSectionSerializer(hero_obj, context={"request": request}).data
            if hero_obj else None
        )

        footer = FooterColumn.objects.filter(is_active=True).order_by("order")
        footer_ser = FooterColumnSerializer(
            footer,
            many=True,
            context={"request": request}
        ).data

        sections = HomeSection.objects.filter(is_active=True).order_by("order")
        sec_ser = PublicHomeSectionSerializer(sections, many=True).data

        return Response({
            "hero": hero_data,
            "footer_columns": footer_ser,
            "sections": sec_ser,
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

    def get(self, request):
        links = HeaderLink.objects.all().order_by("order")
        return Response(HeaderLinkSerializer(links, many=True).data)

    def post(self, request):
        # منع أكثر من شعار
        if request.data.get("type") == "logo":
            HeaderLink.objects.filter(type="logo").delete()

        ser = HeaderLinkSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)

        return Response(ser.errors, status=400)


class HeaderLinkDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        link = get_object_or_404(HeaderLink, pk=pk)
        ser = HeaderLinkSerializer(link, data=request.data, partial=True)

        if ser.is_valid():
            ser.save()
            return Response(ser.data)

        return Response(ser.errors, status=400)

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
        Q(title_ar__icontains=q) | Q(title_en__icontains=q),
        is_published=True,
        show_in_sitemap=True
    )

    for p in pages:
        results.append({
            "type": "page",
            "title": p.title_ar if lang == "ar" else p.title_en,
            "url": f"/page/{p.slug}"
        })

    # ================= Blog =================
    blogs = BlogPost.objects.filter(
        Q(title_ar__icontains=q) | Q(title_en__icontains=q),
        status="published"
    )

    for b in blogs:
        results.append({
            "type": "blog",
            "title": b.title_ar if lang == "ar" else b.title_en,
            "url": f"/blog/{b.slug}"
        })

    # ================= Services =================
    services = Service.objects.filter(
        Q(title_ar__icontains=q) | Q(title_en__icontains=q),
        is_active=True
    )

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
        faqs = FAQItem.objects.filter(is_active=True).order_by("order")
        ser = FAQItemSerializer(faqs, many=True)
        return Response(ser.data)


# ================== ADMIN FAQ ==================

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

        cards = ContactCard.objects.all().order_by("order")
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
        page, _ = PageContent.objects.get_or_create(slug=slug)
        return Response(PageContentSerializer(page).data)


class AdminPageContentView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, slug):
        page, _ = PageContent.objects.get_or_create(slug=slug)
        serializer = PageContentSerializer(page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
