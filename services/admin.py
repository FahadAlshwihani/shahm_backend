from django.contrib import admin
from .models import (
    PracticeArea,
    Service,
    ServiceAdvisoryPage,
    ServiceAdvisoryRequest,
    ServiceAdvisoryRequestItem,
    AppointmentSettings,
    AppointmentSlot,
    AppointmentBooking,
)


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


@admin.register(PracticeArea)
class PracticeAreaAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "is_active", "show_on_home", "order")
    list_editable = ("is_active", "show_on_home", "order")
    search_fields = ("name_ar", "name_en")
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title_ar", "practice_area", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title_ar", "title_en")
    list_filter = ("practice_area",)


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
        "get_services",
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

    def get_services(self, obj):
        return ", ".join([item.service.title_en for item in obj.items.all()])

    get_services.short_description = "Services"


@admin.register(AppointmentSettings)
class AppointmentSettingsAdmin(admin.ModelAdmin):
    list_display = ["price_in_person", "price_online", "slot_duration", "is_active"]


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "is_available")
    list_filter = ("date", "is_available")


@admin.register(AppointmentBooking)
class AppointmentBookingAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "slot", "status", "created_at")
    list_filter = ("status",)
