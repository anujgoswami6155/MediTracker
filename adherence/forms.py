from django import forms
from .models import IntakeLog, Reminder
from schedules.models import MedicineSchedule


class IntakeLogForm(forms.ModelForm):
    """Form for logging medicine intake"""
    
    class Meta:
        model = IntakeLog
        fields = ['schedule', 'patient', 'date', 'status', 'taken_at']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
            'taken_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
        }
        labels = {
            'schedule': 'Medicine Schedule',
            'date': 'Date',
            'status': 'Status (Taken/Missed/Skipped)',
            'taken_at': 'Actual Time Taken (Optional)',
        }
    
    def __init__(self, patient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hide patient field (we set it in the view)
        self.fields["patient"].required = False
        self.fields["patient"].widget = forms.HiddenInput()
        
        # Patient can only select their own schedules
        if patient:
            self.fields["schedule"].queryset = MedicineSchedule.objects.filter(
                prescription_item__prescription__patient=patient,
                is_active=True
            ).select_related('prescription_item__medicine')
            
            # Make the display more user-friendly
            self.fields["schedule"].label_from_instance = lambda obj: (
                f"{obj.prescription_item.medicine.name} at {obj.time}"
            )


class ReminderForm(forms.ModelForm):
    """Form for creating medicine reminders"""
    
    class Meta:
        model = Reminder
        fields = ['schedule', 'reminder_time', 'is_active']
        widgets = {
            'reminder_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
        }
        labels = {
            'schedule': 'Medicine Schedule',
            'reminder_time': 'Reminder Time',
            'is_active': 'Active Reminder?',
        }
    
    def __init__(self, patient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Patient can only select their own schedules
        if patient:
            self.fields["schedule"].queryset = MedicineSchedule.objects.filter(
                prescription_item__prescription__patient=patient,
                is_active=True
            ).select_related('prescription_item__medicine')
            
            # Make the display more user-friendly
            self.fields["schedule"].label_from_instance = lambda obj: (
                f"{obj.prescription_item.medicine.name} at {obj.time}"
            )