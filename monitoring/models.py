from django.db import models
from django.conf import settings


class FamilyMonitoring(models.Model):
    family_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_monitoring",
        limit_choices_to={"role": "family"},
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monitored_by",
        limit_choices_to={"role": "patient"},
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("family_member", "patient")

    def __str__(self):
        return f"{self.family_member} monitors {self.patient}"
