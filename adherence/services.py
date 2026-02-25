from datetime import timedelta
from django.utils import timezone
from .models import IntakeLog

def get_adherence_stats(patient_user, days=7):
    """
    Returns adherence stats for a patient for last `days`
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    logs = IntakeLog.objects.filter(
        patient=patient_user,
        date__range=(start_date, end_date),
    )

    total = logs.count()
    taken = logs.filter(status="taken").count()
    missed = logs.filter(status__in=["missed", "skipped"]).count()

    if total == 0:
        adherence = None
    else:
        adherence = round((taken / total) * 100, 1)

    return {
        "total": total,
        "taken": taken,
        "missed": missed,
        "adherence": adherence,
    }