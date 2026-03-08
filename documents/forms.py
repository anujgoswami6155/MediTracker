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
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., Blood Test Report - Jan 2024'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg',
                'rows': 4,
                'placeholder': 'Add any notes about this document...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hide patient field - it will be set automatically in the view
        self.fields["patient"].required = False
        self.fields["patient"].widget = forms.HiddenInput()