from django.contrib import admin
from .models import FamilyMonitoring


@admin.register(FamilyMonitoring)
class FamilyMonitoringAdmin(admin.ModelAdmin):
    list_display = ("id", "family_member", "patient", "created_at")
    search_fields = ("family_member__username", "patient__username")
