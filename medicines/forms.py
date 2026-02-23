from django import forms
from .models import Medicine, Prescription, PrescriptionItem


class MedicineForm(forms.ModelForm):
    """Form for adding/editing medicines in the catalog"""
    
    class Meta:
        model = Medicine
        fields = ['name', 'generic_name', 'strength', 'form', 'manufacturer']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Paracetamol'}),
            'generic_name': forms.TextInput(attrs={'placeholder': 'e.g., Acetaminophen'}),
            'strength': forms.TextInput(attrs={'placeholder': 'e.g., 500mg'}),
            'form': forms.TextInput(attrs={'placeholder': 'e.g., Tablet, Syrup, Capsule'}),
            'manufacturer': forms.TextInput(attrs={'placeholder': 'e.g., Cipla'}),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions"""
    
    class Meta:
        model = Prescription
        fields = ['doctor', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
        }
    
    def __init__(self, patient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter doctors only
        from accounts.models import User
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        
        # Set patient automatically if provided
        if patient:
            self.patient = patient


class PrescriptionItemForm(forms.ModelForm):
    """Form for adding medicines to a prescription"""
    
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'dose', 'unit', 'frequency', 'instructions']
        widgets = {
            'dose': forms.TextInput(attrs={'placeholder': 'e.g., 1'}),
            'unit': forms.TextInput(attrs={'placeholder': 'e.g., tablet, ml'}),
            'frequency': forms.TextInput(attrs={'placeholder': 'e.g., BD (twice daily), TDS (thrice daily)'}),
            'instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Take after meals'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active medicines
        self.fields['medicine'].queryset = Medicine.objects.filter(is_active=True)