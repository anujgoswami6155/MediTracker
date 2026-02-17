from django import forms
from .models import Appointment

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "appointment_time", "reason"]


class AppointmentDoctorUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status", "appointment_date", "appointment_time", "reason"]
