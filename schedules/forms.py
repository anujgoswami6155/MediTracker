from django import forms
from .models import MedicineSchedule
from medicines.models import PrescriptionItem


class MedicineScheduleForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["prescription_item"].queryset = PrescriptionItem.objects.filter(
            prescription__patient=user
        )

    class Meta:
        model = MedicineSchedule
        fields = [
            "prescription_item",
            "start_date",
            "end_date",
            "time",
            "repeat_daily",
            "is_active",
        ]
