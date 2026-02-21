from django import forms
from .models import PatientProfile


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'phone',
            'date_of_birth',
            'gender',
            'blood_group',
            'allergies',
            'chronic_conditions'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
        }