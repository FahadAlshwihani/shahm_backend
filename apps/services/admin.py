from django.contrib import admin

from .models import (
    MainService,
    Service,
    ServiceSection,
    ServicePageCMS,
    ServiceAdvisoryPage,
    ServiceAdvisoryRequest,
    ServiceAdvisoryRequestItem,
    AppointmentSettings,
    AppointmentSlot,
    AppointmentBooking,
)


class ServiceSectionInline(admin.TabularInline):
    model = ServiceSection
    extra = 1


@admin.register(MainService)
class MainServiceAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "title_en",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "code",
        "title_ar",
        "title_en",
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "serial_number",
        "title_en",
        "main_service",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "main_service",
        "is_active",
    )

    search_fields = (
        "serial_number",
        "title_ar",
        "title_en",
    )

    inlines = [ServiceSectionInline]


@admin.register(ServicePageCMS)
class ServicePageCMSAdmin(admin.ModelAdmin):

    list_display = (
        "title_en",
        "primary_action_type",
        "is_active",
    )


@admin.register(ServiceAdvisoryPage)
class ServiceAdvisoryPageAdmin(admin.ModelAdmin):
    pass


class ServiceAdvisoryRequestItemInline(admin.TabularInline):
    model = ServiceAdvisoryRequestItem
    extra = 0
    readonly_fields = ("service",)


@admin.register(ServiceAdvisoryRequest)
class ServiceAdvisoryRequestAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "email",
        "status",
        "created_at",
    )

    list_filter = ("status",)

    search_fields = (
        "first_name",
        "last_name",
        "email",
    )

    inlines = [ServiceAdvisoryRequestItemInline]


@admin.register(AppointmentSettings)
class AppointmentSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "default_price",
        "slot_duration",
        "is_active",
    )

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "start_time",
        "end_time",
        "is_available",
    )

    list_filter = (
        "date",
        "is_available",
    )


@admin.register(AppointmentBooking)
class AppointmentBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference",
        "slot",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "reference",
    )

    readonly_fields = (
        "reference",
        "created_at",
    )