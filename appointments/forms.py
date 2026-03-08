from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentRequestForm(forms.ModelForm):
    
    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "appointment_time", "reason"]
        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
                'min': timezone.now().date().isoformat()  # Prevent past dates
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
                'step': '900'  # 15-minute intervals (900 seconds)
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
                'rows': 4,
                'placeholder': 'Please describe the reason for your appointment...'
            }),
            'doctor': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
        }
        labels = {
            'doctor': 'Select Doctor',
            'appointment_date': 'Appointment Date',
            'appointment_time': 'Appointment Time',
            'reason': 'Reason for Appointment',
        }
        help_texts = {
            'appointment_time': 'Office hours: 7:00 AM - 8:00 PM (Lunch break: 1:00 PM - 2:00 PM)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter to only show doctors
        from accounts.models import User
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        
        # Customize doctor display
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.username}"

    def clean(self):
        cleaned_data = super().clean()

        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        # If fields are missing, skip validation
        if not appointment_date or not appointment_time:
            return cleaned_data

        # Check if appointment is in the past
        now = timezone.now()
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(appointment_date, appointment_time)
        )

        if appointment_datetime < now:
            raise forms.ValidationError(
                "You cannot create an appointment for a past date or time."
            )

        return cleaned_data


class AppointmentDoctorUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Appointment
        fields = ["status", "appointment_date", "appointment_time", "reason"]
        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
                'step': '900'  # 15-minute intervals
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]',
                'rows': 4,
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3F8F6B]'
            }),
        }
        labels = {
            'status': 'Appointment Status',
            'appointment_date': 'Date',
            'appointment_time': 'Time',
            'reason': 'Reason',
        }