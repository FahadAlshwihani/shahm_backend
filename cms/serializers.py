from rest_framework import serializers
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


# ============================================================
# Utility Mixin لحماية الحقول البوليانية من إعادة الضبط
# ============================================================
class PreserveBooleanFieldsMixin:
    """
    يمنع فقدان قيم الحقول البوليانية عندما لا يتم إرسالها أثناء PATCH.
    """
    boolean_fields = []

    def update(self, instance, validated_data):
        for field in self.boolean_fields:
            if field not in validated_data:
                validated_data[field] = getattr(instance, field)
        return super().update(instance, validated_data)


# ============================================================
# HERO MEDIA
# ============================================================
class HeroMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = HeroMedia
        fields = [
            "id",
            "hero",
            "media_type",
            "file",
            "file_url",
            "order",
            "is_active",
        ]
        extra_kwargs = {
            "hero": {"required": False},
            "is_active": {"required": False},
        }

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url





# ============================================================
# HERO SECTION
# ============================================================
class HeroSectionSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    media = HeroMediaSerializer(many=True, read_only=True)

    # لإرجاع slug الصفحات في الـ API العام
    left_page_slug = serializers.CharField(
        source="left_button_page.slug", read_only=True
    )
    right_page_slug = serializers.CharField(
        source="right_button_page.slug", read_only=True
    )
    center_page_slug = serializers.CharField(
        source="center_button_page.slug", read_only=True
    )

    boolean_fields = ["is_active", "show_header"]

    class Meta:
        model = HeroSection
        fields = "__all__"
        extra_kwargs = {
            "is_active": {"required": False},
            "show_header": {"required": False},
        }


# ============================================================
# PAGE
# ============================================================
class PageSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    boolean_fields = ["is_published", "show_in_sitemap"]

    class Meta:
        model = Page
        fields = "__all__"
        extra_kwargs = {
            "is_published": {"required": False, "default": True},
            "show_in_sitemap": {"required": False, "default": True},
        }



# ============================================================
# FOOTER LINK
# ============================================================
class FooterLinkSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    display_label = serializers.SerializerMethodField()
    is_coming_soon = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    resolved_url = serializers.SerializerMethodField()

    boolean_fields = ["is_active"]

    class Meta:
        model = FooterLink
        fields = "__all__"

    def get_display_label(self, obj):
        request = self.context.get("request")
        lang = request.headers.get("Accept-Language", "ar")[:2] if request else "ar"
        return obj.label_en if lang == "en" and obj.label_en else obj.label_ar


    def get_children(self, obj):
        return FooterLinkSerializer(
            obj.children.filter(is_active=True).order_by("order"),
            many=True,
            context=self.context
        ).data

    def get_is_coming_soon(self, obj):
        page = obj.page
        return page.page_status == "coming_soon" if page else False

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_resolved_url(self, obj):
        if obj.page:
            return f"/page/{obj.page.slug}"
        return obj.url or ""

    def get_lang(self):
        request = self.context.get("request")
        if not request:
            return "ar"
        return request.headers.get("Accept-Language", "ar")[:2]


# ============================================================
# FOOTER COLUMN
# ============================================================
class FooterColumnSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = FooterColumn
        fields = "__all__"

    def get_links(self, obj):
        return FooterLinkSerializer(
            obj.links.filter(parent__isnull=True, is_active=True),
            many=True,
            context=self.context
        ).data




# ============================================================
# HOME SECTION
# ============================================================
class HomeSectionSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    boolean_fields = ["is_active"]

    class Meta:
        model = HomeSection
        fields = "__all__"
        extra_kwargs = {
            "is_active": {"required": False},
        }


class PublicHomeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSection
        fields = "__all__"


# ============================================================
# HEADER LINK
# ============================================================
class HeaderLinkSerializer(PreserveBooleanFieldsMixin, serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    resolved_url = serializers.SerializerMethodField()

    boolean_fields = ["is_active"]

    class Meta:
        model = HeaderLink
        fields = "__all__"

    def get_children(self, obj):
        return HeaderLinkSerializer(obj.children.all(), many=True).data

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None

    def get_resolved_url(self, obj):
        if obj.page:
            return f"/page/{obj.page.slug}"
        return obj.url or ""



# ============================================================
# FAQ
# ============================================================

class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = "__all__"
        extra_kwargs = {
            "is_active": {"required": False},
        }


# ================== Contact Page ==================


class ContactFAQPreviewSerializer(serializers.ModelSerializer):
    faq = FAQItemSerializer(read_only=True)

    class Meta:
        model = ContactFAQPreview
        fields = "__all__"

class ContactCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCard
        fields = "__all__"


class ContactPageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPageSettings
        fields = "__all__"



class PageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContent
        fields = "__all__"
