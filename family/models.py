from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class FamilyPatientLink(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    family_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_links",
        limit_choices_to={"role": "family"},
    )

    patient = models.ForeignKey(
        "patients.PatientProfile",
        on_delete=models.CASCADE,
        related_name="family_links",
    )

    relation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Father, Mother, Guardian, Caregiver etc."
    )

    # ✅ NEW (required for Option 2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # ✅ active ONLY after approval
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("family_member", "patient")

    def __str__(self):
        return f"{self.family_member} → {self.patient} ({self.status})"