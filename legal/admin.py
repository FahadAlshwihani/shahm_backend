from django.contrib import admin
from .models import LegalPage

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title_ar", "is_published", "show_in_footer", "updated_at")
    list_editable = ("is_published", "show_in_footer")
    search_fields = ("slug", "title_ar", "title_en")
