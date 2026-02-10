from django.db import models
from django.conf import settings

class Medicine(models.Model):
    name = models.CharField(max_length=120)
    generic_name = models.CharField(max_length=120, blank=True)
    strength = models.CharField(max_length=50, blank=True)   # e.g. 500mg
    form = models.CharField(max_length=50, blank=True)       # tablet/syrup
    manufacturer = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.strength}".strip()


class Prescription(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions_as_patient",
        limit_choices_to={"role": "patient"},
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="prescriptions_as_doctor",
        limit_choices_to={"role": "doctor"},
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription #{self.id}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    dose = models.CharField(max_length=50)              # e.g. 1
    unit = models.CharField(max_length=20, blank=True)  # tablet/ml/mg
    frequency = models.CharField(max_length=30)         # OD/BD/TDS
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medicine} ({self.frequency})"
