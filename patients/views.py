from django.shortcuts import render, redirect,get_object_or_404
from core.decorators import role_required
from .models import PatientProfile
from .forms import PatientProfileForm
from family.models import FamilyPatientLink
from django.contrib import messages

@role_required("patient")
def dashboard(request):
    """Patient dashboard - overview of everything"""
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    
    # Import here to avoid circular imports
    from schedules.models import MedicineSchedule
    from adherence.models import IntakeLog
    from documents.models import MedicalDocument
    from appointments.models import Appointment
    
    # Get recent data
    upcoming_schedules = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient=request.user,
        is_active=True
    ).order_by('time')[:5]
    
    recent_logs = IntakeLog.objects.filter(
        patient=request.user
    ).order_by('-created_at')[:5]
    
    my_documents = MedicalDocument.objects.filter(
        patient=request.user,
        is_active=True
    ).count()
    
    my_appointments = Appointment.objects.filter(
        patient=request.user
    ).exclude(status__in=['completed', 'cancelled']).count()
    
    context = {
        'patient': profile,
        'upcoming_schedules': upcoming_schedules,
        'recent_logs': recent_logs,
        'documents_count': my_documents,
        'appointments_count': my_appointments,
    }
    
    return render(request, 'patients/dashboard.html', context)


@role_required("patient")
def profile_view(request):
    """View patient profile"""
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'patients/profile.html', {'profile': profile})


@role_required("patient")
def profile_edit(request):
    """Edit patient profile"""
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('patients:profile')
    else:
        form = PatientProfileForm(instance=profile)
    
    return render(request, 'patients/profile_edit.html', {'form': form})

@role_required("patient")
def dependent_requests(request):
    """
    Patient can see all pending family access requests
    """
    requests = FamilyPatientLink.objects.filter(
        patient__user=request.user,
        status="pending"
    ).select_related("family_member")

    return render(
        request,
        "patients/dependent_requests.html",
        {"requests": requests}
    )


@role_required("patient")
def respond_dependent_request(request, pk, action):
    """
    Patient approves or rejects dependent request
    """
    link = get_object_or_404(
        FamilyPatientLink,
        pk=pk,
        patient__user=request.user
    )

    if action == "approve":
        link.status = "approved"
        link.is_active = True

    elif action == "reject":
        link.status = "rejected"
        link.is_active = False

    link.save()
    return redirect("patients:dependent_requests")



@role_required("patient")
def dependent_requests(request):

    requests = FamilyPatientLink.objects.filter(
        patient=request.user.patient_profile,
        status="pending"
    ).select_related("family_member")

    return render(
        request,
        "patients/dependent_requests.html",
        {"requests": requests}
    )

@role_required("patient")
def handle_dependent_request(request, pk, action):

    link = get_object_or_404(
        FamilyPatientLink,
        pk=pk,
        patient=request.user.patient_profile,
        status="pending"
    )

    if action == "approve":
        link.status = "approved"
        link.is_active = True
        link.save(update_fields=["status", "is_active"])

        messages.success(
            request,
            f"{link.family_member.username} is now linked to your account."
        )

    elif action == "reject":
        link.status = "rejected"
        link.is_active = False
        link.save(update_fields=["status", "is_active"])

        messages.info(
            request,
            "Dependent request rejected."
        )

    return redirect("patients:dependent_requests")