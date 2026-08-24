from django.contrib import admin
from .models import TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name_ar", "name_en")
