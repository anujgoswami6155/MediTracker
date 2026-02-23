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

    
    start_of_week = today_date - timedelta(days=today_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    qs = Appointment.objects.filter(doctor=doctor)

    pending = qs.filter(status="requested").count()


    today = qs.filter(appointment_date=today_date).exclude(status="cancelled").count()

    approved_this_week = qs.filter(
        status="approved",
        appointment_date__range=[start_of_week, end_of_week]
    ).count()

    approved = qs.filter(status="approved").count()

    unread_alerts = 0

    context = {
        "pending": pending,
        "today": today,
        "approved": approved,                 # old (kept)
        "approved_this_week": approved_this_week,
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