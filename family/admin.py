# family/admin.py
from django.contrib import admin
from .models import FamilyPatientLink

@admin.register(FamilyPatientLink)
class FamilyPatientLinkAdmin(admin.ModelAdmin):
    list_display = ("family_member", "patient", "relation", "is_active")
    list_filter = ("is_active",)