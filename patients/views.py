from django.shortcuts import render
from core.decorators import role_required
from .models import PatientProfile

@role_required("patient")
def dashboard(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, "patients/dashboard.html", {"patient": profile})
