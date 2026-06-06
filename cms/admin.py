from django.contrib import admin
from .models import *

# ===========================
# HERO
# ===========================

class HeroMediaInline(admin.TabularInline):
    model = HeroMedia
    extra = 0


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "show_header",
        "is_active",
        "order",
    )
    list_editable = (
        "show_header",
        "is_active",
        "order",
    )
    search_fields = ("slug",)
    ordering = ("order",)
    inlines = [HeroMediaInline]


@admin.register(HeroMedia)
class HeroMediaAdmin(admin.ModelAdmin):
    list_display = (
        "hero",
        "media_type",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


# ===========================
# PAGES
# ===========================

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title_ar",
        "page_status",
        "is_published",
        "show_in_sitemap",
        "updated_at",
    )
    list_editable = (
        "page_status",
        "is_published",
        "show_in_sitemap",
    )
    search_fields = (
        "slug",
        "title_ar",
        "title_en",
    )


# ===========================
# FOOTER
# ===========================

class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 0


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = (
        "title_ar",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )
    inlines = [FooterLinkInline]


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = (
        "label_ar",
        "column",
        "parent",
        "media_type",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(FooterCTA)
class FooterCTAAdmin(admin.ModelAdmin):
    list_display = (
        "title_ar",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


# ===========================
# HOME
# ===========================

@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "title_ar",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


# ===========================
# HEADER
# ===========================

@admin.register(HeaderLink)
class HeaderLinkAdmin(admin.ModelAdmin):
    list_display = (
        "label_ar",
        "type",
        "parent",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


# ===========================
# FAQ
# ===========================

class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 0


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title_ar",
        "slug",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )
    inlines = [FAQItemInline]


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = (
        "question_ar",
        "category",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


# ===========================
# CONTACT
# ===========================

@admin.register(ContactCard)
class ContactCardAdmin(admin.ModelAdmin):
    list_display = (
        "title_ar",
        "type",
        "order",
        "is_active",
    )
    list_editable = (
        "order",
        "is_active",
    )


@admin.register(ContactFAQPreview)
class ContactFAQPreviewAdmin(admin.ModelAdmin):
    list_display = (
        "faq",
        "order",
        "is_active",
    )


@admin.register(ContactPageSettings)
class ContactPageSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "updated_at",
    )


# ===========================
# ABOUT
# ===========================

class AboutStatInline(admin.TabularInline):
    model = AboutStat
    extra = 0


class AboutPostInline(admin.TabularInline):
    model = AboutPost
    extra = 0


class AboutSectionInline(admin.TabularInline):
    model = AboutSection
    extra = 0


class AboutPartnerInline(admin.TabularInline):
    model = AboutPartner
    extra = 0


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [
        AboutStatInline,
        AboutPostInline,
        AboutSectionInline,
        AboutPartnerInline,
    ]


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutPost)
class AboutPostAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutIcon)
class AboutIconAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutPartner)
class AboutPartnerAdmin(admin.ModelAdmin):
    pass