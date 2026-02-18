from django import forms
from .models import MedicalDocument


class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = [
            "patient",
            "document_type",
            "title",
            "file",
            "notes",
        ]
