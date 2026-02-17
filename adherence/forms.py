from django import forms
from .models import IntakeLog, Reminder
from schedules.models import MedicineSchedule


class IntakeLogForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # hide patient (we set it in view)
        self.fields["patient"].required = False
        self.fields["patient"].widget = forms.HiddenInput()

        # patient can only select their own schedules
        self.fields["schedule"].queryset = MedicineSchedule.objects.filter(
            prescription_item__prescription__patient=user
        )

    class Meta:
        model = IntakeLog
        fields = ["schedule", "date", "status", "taken_at"]  # patient auto


class ReminderForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # patient can only select their own schedules
        self.fields["schedule"].queryset = MedicineSchedule.objects.filter(
            prescription_item__prescription__patient=user
        )

    class Meta:
        model = Reminder
        fields = ["schedule", "reminder_time", "is_active"]
