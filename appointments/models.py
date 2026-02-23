from django.db import models
from django.conf import settings


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_patient",
        limit_choices_to={"role": "patient"},
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="appointments_as_doctor",
        limit_choices_to={"role": "doctor"},
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    reason = models.TextField(blank=True)

    # ✅ ADD THIS
    doctor_notes = models.TextField(blank=True, null=True)

    # (Optional but Professional)
    follow_up_date = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.status})"