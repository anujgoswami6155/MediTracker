from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from appointments.models import Appointment


# 🔹 Patient Dashboard
@login_required
@role_required("patient")
def patient_dashboard(request):
    return render(request, "core/patient_dashboard.html")


# 🔹 Doctor Dashboard
@login_required
@role_required("doctor")
def doctor_dashboard(request):
    doctor = request.user

    pending = Appointment.objects.filter(
        doctor=doctor,
        status="requested"
    ).count()

    today = Appointment.objects.filter(
        doctor=doctor
    ).count()

    approved = Appointment.objects.filter(
        doctor=doctor,
        status="approved"
    ).count()

    context = {
        "pending": pending,
        "today": today,
        "approved": approved,
    }

    return render(request, "doctor/doctor_dashboard.html", context)



# 🔹 Family Dashboard
@login_required
@role_required("family")
def family_dashboard(request):
    return render(request, "core/family_dashboard.html")
