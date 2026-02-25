from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentRequestForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "appointment_time", "reason"]

    def clean(self):
        cleaned_data = super().clean()

        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        # If fields are missing, skip validation
        if not appointment_date or not appointment_time:
            return cleaned_data

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