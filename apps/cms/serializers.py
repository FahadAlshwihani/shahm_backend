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
    FooterSettings,
    FooterCTA,
    FAQCategory,
    AboutStat,
    AboutPost,
    AboutIcon,
    AboutSection,
    AboutPartner,
    AboutPage,
)
from apps.form_builder.serializers import InfoModalSerializer
from apps.form_builder.models import InfoModal


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

    left_resolved_url = serializers.SerializerMethodField()
    right_resolved_url = serializers.SerializerMethodField()

    boolean_fields = ["is_active", "show_header"]

    class Meta:
        model = HeroSection
        fields = "__all__"
        extra_kwargs = {
            "is_active": {"required": False},
            "show_header": {"required": False},
        }

    def get_left_resolved_url(self, obj):
        if obj.left_button_page:
            return f"/page/{obj.left_button_page.slug}"

        if obj.left_button_slug:
            return obj.left_button_slug

        return obj.left_button_url or ""

    def get_right_resolved_url(self, obj):
        if obj.right_button_page:
            return f"/page/{obj.right_button_page.slug}"

        if obj.right_button_slug:
            return obj.right_button_slug

        return obj.right_button_url or ""


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
            obj.links.filter(
                parent__isnull=True,
                is_active=True
            ).prefetch_related("children"),
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
class HeaderLinkSerializer(
    PreserveBooleanFieldsMixin,
    serializers.ModelSerializer
):
    children = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    resolved_url = serializers.SerializerMethodField()
    boolean_fields = ["is_active"]

    class Meta:
        model = HeaderLink
        fields = "__all__"

    def get_children(self, obj):
        return HeaderLinkSerializer(
            obj.children.filter(is_active=True).order_by("order"),
            many=True,
            context=self.context
        ).data

    def get_logo_url(self, obj):
        if not obj.logo:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_resolved_url(self, obj):

        if obj.page:
            return f"/page/{obj.page.slug}"

        if obj.slug:
            return obj.slug

        return obj.url or ""

    def validate(self, data):

        # limit quick access buttons
        if data.get("type") == "quick_access":

            qs = HeaderLink.objects.filter(type="quick_access")

            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.count() >= 8:
                raise serializers.ValidationError(
                    "max 8 quick access buttons"
                )

        return data


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


class FAQCategorySerializer(serializers.ModelSerializer):
    faqs = FAQItemSerializer(many=True, read_only=True)
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = FAQCategory
        fields = [
            "id",
            "title_ar",
            "title_en",
            "slug",
            "icon",
            "icon_url",
            "faqs",
            "order",
            "is_active",
        ]

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None


# ================== Contact Page ==================


class ContactFAQPreviewSerializer(serializers.ModelSerializer):
    faq = FAQItemSerializer(read_only=True)

    class Meta:
        model = ContactFAQPreview
        fields = "__all__"


class ContactCardSerializer(serializers.ModelSerializer):
    # =========================
    # FORMS
    # =========================

    primary_form_slug = serializers.CharField(
        source="primary_form.slug",
        read_only=True,
    )

    secondary_form_slug = serializers.CharField(
        source="secondary_form.slug",
        read_only=True,
    )

    # =========================
    # INFO MODALS (READ)
    # =========================

    primary_info_modal = InfoModalSerializer(
        read_only=True,
    )

    secondary_info_modal = InfoModalSerializer(
        read_only=True,
    )

    # =========================
    # INFO MODALS (WRITE)
    # =========================

    primary_info_modal_id = serializers.PrimaryKeyRelatedField(
        source="primary_info_modal",
        queryset=InfoModal.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    secondary_info_modal_id = serializers.PrimaryKeyRelatedField(
        source="secondary_info_modal",
        queryset=InfoModal.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ContactCard
        fields = "__all__"

    def validate(self, data):

        instance = getattr(self, "instance", None)

        primary_action_type = data.get(
            "primary_action_type",
            getattr(instance, "primary_action_type", "none"),
        )

        secondary_action_type = data.get(
            "secondary_action_type",
            getattr(instance, "secondary_action_type", "none"),
        )

        primary_url = data.get(
            "primary_url",
            getattr(instance, "primary_url", ""),
        )

        secondary_url = data.get(
            "secondary_url",
            getattr(instance, "secondary_url", ""),
        )

        primary_form = data.get(
            "primary_form",
            getattr(instance, "primary_form", None),
        )

        secondary_form = data.get(
            "secondary_form",
            getattr(instance, "secondary_form", None),
        )

        primary_info_modal = data.get(
            "primary_info_modal",
            getattr(instance, "primary_info_modal", None),
        )

        secondary_info_modal = data.get(
            "secondary_info_modal",
            getattr(instance, "secondary_info_modal", None),
        )

        # =========================
        # PRIMARY
        # =========================

        if primary_action_type == "url" and not primary_url:
            raise serializers.ValidationError({
                "primary_url": "required"
            })

        if primary_action_type == "form_modal" and not primary_form:
            raise serializers.ValidationError({
                "primary_form": "required"
            })

        if primary_action_type == "info_modal" and not primary_info_modal:
            raise serializers.ValidationError({
                "primary_info_modal_id": "required"
            })

        # =========================
        # SECONDARY
        # =========================

        if secondary_action_type == "url" and not secondary_url:
            raise serializers.ValidationError({
                "secondary_url": "required"
            })

        if secondary_action_type == "form_modal" and not secondary_form:
            raise serializers.ValidationError({
                "secondary_form": "required"
            })

        if secondary_action_type == "info_modal" and not secondary_info_modal:
            raise serializers.ValidationError({
                "secondary_info_modal_id": "required"
            })

        # =========================
        # CLEANUP
        # =========================

        if primary_action_type != "url":
            data["primary_url"] = ""

        if primary_action_type != "form_modal":
            data["primary_form"] = None

        if primary_action_type != "info_modal":
            data["primary_info_modal"] = None

        if secondary_action_type != "url":
            data["secondary_url"] = ""

        if secondary_action_type != "form_modal":
            data["secondary_form"] = None

        if secondary_action_type != "info_modal":
            data["secondary_info_modal"] = None

        return data


class ContactPageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPageSettings
        fields = "__all__"


class PageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContent
        fields = "__all__"


class FooterSettingsSerializer(serializers.ModelSerializer):
    logo_ar_url = serializers.SerializerMethodField()
    logo_en_url = serializers.SerializerMethodField()
    vat_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = FooterSettings
        fields = "__all__"

    def _build_url(self, file):
        if not file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(file.url)

        return file.url

    def get_logo_ar_url(self, obj):
        return self._build_url(obj.logo_ar)

    def get_logo_en_url(self, obj):
        return self._build_url(obj.logo_en)

    def get_vat_logo_url(self, obj):
        return self._build_url(obj.vat_logo)


class FooterCTASerializer(serializers.ModelSerializer):
    resolved_url = serializers.SerializerMethodField()

    class Meta:
        model = FooterCTA

        fields = "__all__"

    def get_resolved_url(self, obj):
        if obj.page:
            return f"/page/{obj.page.slug}"

        return obj.url or ""


class AboutStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutStat
        fields = "__all__"
        extra_kwargs = {
            "page": {"required": False},
        }


class AboutPostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutPost
        fields = "__all__"
        extra_kwargs = {
            "page": {"required": False},
        }

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return None


class AboutIconSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutIcon
        fields = "__all__"

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        if obj.icon:
            return obj.icon.url
        return None


class AboutSectionSerializer(serializers.ModelSerializer):
    icons = AboutIconSerializer(many=True, read_only=True)

    class Meta:
        model = AboutSection
        fields = "__all__"
        extra_kwargs = {
            "page": {"required": False},
        }


class AboutPartnerSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutPartner
        fields = ["id", "page", "logo", "logo_url", "order"]
        extra_kwargs = {
            "page": {"required": False},
        }

    def get_logo_url(self, obj):
        request = self.context.get("request")

        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)

        if obj.logo:
            return obj.logo.url

        return None


class AboutPageSerializer(serializers.ModelSerializer):
    stats = AboutStatSerializer(many=True, read_only=True)
    posts = AboutPostSerializer(many=True, read_only=True)
    sections = AboutSectionSerializer(many=True, read_only=True)
    partners = AboutPartnerSerializer(many=True, read_only=True)

    media_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    mobile_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = "__all__"

    def get_media_url(self, obj):
        if not obj.media:
            return None
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.media.url)

        return obj.media.url

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.logo.url)

        return obj.logo.url

    def get_mobile_logo_url(self, obj):
        if not obj.mobile_logo:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.mobile_logo.url
            )

        return obj.mobile_logo.url
