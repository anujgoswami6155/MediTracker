from django.contrib import admin
from .models import DoctorInstruction


@admin.register(DoctorInstruction)
class DoctorInstructionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "patient", "doctor", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "patient__username", "doctor__username")
