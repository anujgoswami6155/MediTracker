from django.contrib import admin
from .models import Medicine, Prescription, PrescriptionItem

admin.site.register(Medicine)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
