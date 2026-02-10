from django.db import models
from schedules.models import MedicineSchedule
from django.conf import settings


class IntakeLog(models.Model):
    STATUS_CHOICES = (
        ("taken", "Taken"),
        ("missed", "Missed"),
        ("skipped", "Skipped"),
    )

    schedule = models.ForeignKey(
        MedicineSchedule,
        on_delete=models.CASCADE,
        related_name="intake_logs"
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "patient"},
    )

    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    taken_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.schedule} - {self.status}"


class Reminder(models.Model):
    schedule = models.ForeignKey(
        MedicineSchedule,
        on_delete=models.CASCADE,
        related_name="reminders"
    )

    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Reminder for {self.schedule} at {self.reminder_time}"
