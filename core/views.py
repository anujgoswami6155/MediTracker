from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import role_required


# 🔹 Patient Dashboard
@login_required
@role_required("patient")
def patient_dashboard(request):
    return render(request, "core/patient_dashboard.html")


# 🔹 Doctor Dashboard
@login_required
@role_required("doctor")
def doctor_dashboard(request):
    return render(request, "core/doctor_dashboard.html")


# 🔹 Family Dashboard
@login_required
@role_required("family")
def family_dashboard(request):
    return render(request, "core/family_dashboard.html")