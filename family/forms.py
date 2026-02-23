# family/forms.py
from django import forms
from .models import FamilyPatientLink

class AddDependentRequestForm(forms.ModelForm):
    class Meta:
        model = FamilyPatientLink
        fields = ["patient", "relation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: better labels
        self.fields["patient"].label = "Select Patient"
        self.fields["relation"].label = "Relation with Patient"