from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from appointments.models import Appointment

@login_required
@role_required("patient")
def patient_dashboard(request):
    return render(request, "core/patient_dashboard.html")


@login_required
@role_required("doctor")
def doctor_dashboard(request):
    doctor = request.user
    today_date = timezone.localdate()

    qs = Appointment.objects.filter(doctor=doctor)

    # Pending (still requested & future/today)
    pending = qs.filter(
        status="requested",
        appointment_date__gte=today_date
    ).count()

    # Today appointments (not cancelled)
    today = qs.filter(
        appointment_date=today_date
    ).exclude(status="cancelled").count()

    # ✅ MISSED = requested but date already gone
    missed = qs.filter(
        status="requested",
        appointment_date__lt=today_date
    ).count()

    approved = qs.filter(status="approved").count()

    unread_alerts = 0

    context = {
        "pending": pending,
        "today": today,
        "approved": approved,
        "missed": missed,
        "unread_alerts": unread_alerts,
    }

    return render(request, "doctor/doctor_dashboard.html", context)


# 🔹 Family Dashboard
@login_required
@role_required("family")
def family_dashboard(request):
    return render(request, "family/dashboard.html")

from django.shortcuts import redirect

def home(request):
    """Smart homepage - redirects based on user status"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # User is logged in - redirect to their dashboard
    if request.user.role == 'patient':
        return redirect('core:patient_dashboard')
    elif request.user.role == 'doctor':
        return redirect('core:doctor_dashboard')
    elif request.user.role == 'family':
        return redirect('family:dashboard')
    
    return redirect('accounts:login')