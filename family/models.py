from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class FamilyPatientLink(models.Model):
    family_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_links",
        limit_choices_to={"role": "family"},
    )

    patient = models.ForeignKey(
        "patients.PatientProfile",   # ✅ CORRECT MODEL NAME
        on_delete=models.CASCADE,
        related_name="family_links",
    )

    relation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Father, Mother, Guardian, Caregiver etc."
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("family_member", "patient")

    def __str__(self):
        return f"{self.family_member} → {self.patient}"