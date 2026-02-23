# family/admin.py
from django.contrib import admin
from .models import FamilyPatientLink

class FamilyPatientLinkAdmin(admin.ModelAdmin):
    list_display = ("family_member", "patient", "relation", "status", "is_active")
    list_filter = ("status", "is_active")

    actions = ["approve_requests"]

    def approve_requests(self, request, queryset):
        queryset.update(status="approved", is_active=True)

    approve_requests.short_description = "Approve selected dependent requests"