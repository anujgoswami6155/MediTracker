from django import forms
from .models import MedicineSchedule
from medicines.models import PrescriptionItem


class MedicineScheduleForm(forms.ModelForm):
    
    class Meta:
        model = MedicineSchedule
        fields = [
            "prescription_item",
            "start_date",
            "end_date",
            "time",
            "repeat_daily",
            "is_active",
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
        }
        labels = {
            'prescription_item': 'Select Medicine (from your prescriptions)',
            'start_date': 'Start Date',
            'end_date': 'End Date (Optional)',
            'time': 'Time to take medicine',
            'repeat_daily': 'Repeat Daily?',
            'is_active': 'Active Schedule?',
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter prescription items to only show this patient's active items
        self.fields["prescription_item"].queryset = PrescriptionItem.objects.filter(
            prescription__patient=user,
            is_active=True
        ).select_related('medicine', 'prescription')
        
        # Make the queryset display more helpful information
        self.fields["prescription_item"].label_from_instance = lambda obj: (
            f"{obj.medicine.name} - {obj.dose} {obj.unit} - {obj.frequency} "
            f"(Prescription #{obj.prescription.id})"
        )