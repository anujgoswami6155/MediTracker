from django.shortcuts import render, redirect
from core.decorators import role_required
from .models import PatientProfile
from .forms import PatientProfileForm


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