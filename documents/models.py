from django.db import models
from django.conf import settings

class MedicalDocument(models.Model):
    DOC_TYPES = (
        ("prescription", "Prescription"),
        ("lab_report", "Lab Report"),
        ("scan", "Scan/X-Ray/MRI"),
        ("discharge", "Discharge Summary"),
        ("other", "Other"),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_documents",
        limit_choices_to={"role": "patient"},
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="uploaded_documents",
    )

    document_type = models.CharField(max_length=30, choices=DOC_TYPES, default="other")
    title = models.CharField(max_length=150, blank=True)
    file = models.FileField(upload_to="documents/")
    notes = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient} - {self.document_type}"
