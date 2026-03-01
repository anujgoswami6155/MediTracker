from django import forms
from .models import IntakeLog, Reminder
from schedules.models import MedicineSchedule


class IntakeLogForm(forms.ModelForm):
    """Form for logging medicine intake"""
    
    class Meta:
        model = IntakeLog
        fields = ['schedule', 'patient', 'date', 'status', 'taken_at']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'taken_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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


class ReminderForm(forms.ModelForm):
    """Form for creating medicine reminders"""
    
    class Meta:
        model = Reminder
        fields = ['schedule', 'reminder_time', 'is_active']
        widgets = {
            'reminder_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, patient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Patient can only select their own schedules
        if patient:
            self.fields["schedule"].queryset = MedicineSchedule.objects.filter(
                prescription_item__prescription__patient=patient,
                is_active=True
            ).select_related('prescription_item__medicine')