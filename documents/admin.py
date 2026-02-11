from django.contrib import admin
from .models import MedicalDocument

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "document_type", "uploaded_at", "is_active")
    list_filter = ("document_type", "is_active", "uploaded_at")
    search_fields = ("patient__username", "title", "notes")