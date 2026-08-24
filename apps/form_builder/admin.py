from django.contrib import admin

from .models import (
    FormTemplate,
    FormSection,
    FormField,
    FormFieldOption,
    FormSubmission,
    FormSubmissionValue,
)


class FormFieldOptionInline(admin.TabularInline):
    model = FormFieldOption
    extra = 0


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0


class FormSectionInline(admin.StackedInline):
    model = FormSection
    extra = 0


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_ar",
        "slug",
        "is_active",
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("title_en",)
    }

    inlines = [
        FormSectionInline,
    ]


@admin.register(FormSection)
class FormSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "form",
        "title_ar",
        "order",
        "is_active",
    )

    inlines = [
        FormFieldInline,
    ]


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "key",
        "field_type",
        "section",
        "required",
        "is_active",
    )

    inlines = [
        FormFieldOptionInline,
    ]


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "form",
        "status",
        "submitted_by",
        "submitted_at",
    )


@admin.register(FormSubmissionValue)
class FormSubmissionValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "field",
    )