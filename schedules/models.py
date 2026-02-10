from django.db import models
from medicines.models import PrescriptionItem

class MedicineSchedule(models.Model):
    prescription_item = models.ForeignKey(
        PrescriptionItem,
        on_delete=models.CASCADE,
        related_name="schedules"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    time = models.TimeField()  

    repeat_daily = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prescription_item} @ {self.time}"
