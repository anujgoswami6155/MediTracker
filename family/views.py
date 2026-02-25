# ===============================
# Django imports
# ===============================
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.db.models import Q

# ===============================
# Core / utils
# ===============================
from core.decorators import role_required
from .utils import (
    is_family_member,
    can_family_access_patient,
    can_family_manage_appointments,
)

# ===============================
# Models
# ===============================
from patients.models import PatientProfile
from medicines.models import Prescription
from schedules.models import MedicineSchedule
from appointments.models import Appointment
from documents.models import MedicalDocument
from adherence.services import get_adherence_stats
from .models import FamilyPatientLink

# ===============================
# Forms
# ===============================
from appointments.forms import AppointmentRequestForm

User = get_user_model()

# ======================================================
# FAMILY DASHBOARD
# ======================================================

@role_required("family")
def family_dashboard(request):
    # -------------------------------
    # Approved dependents
    # -------------------------------
    approved_links = FamilyPatientLink.objects.filter(
        family_member=request.user,
        status="approved",
        is_active=True
    ).select_related("patient__user")

    patients = [link.patient.user for link in approved_links]

    # -------------------------------
    # Pending requests (NEW)
    # -------------------------------
    pending_links = FamilyPatientLink.objects.filter(
        family_member=request.user,
        status="pending"
    ).select_related("patient__user")
       
    rejected_links = FamilyPatientLink.objects.filter(
        family_member=request.user,
        status="rejected"
    ).select_related("patient__user")

    # -------------------------------
    # Upcoming appointments (7 days)
    # -------------------------------
    upcoming_appointments = Appointment.objects.filter(
        patient__in=patients,
        appointment_date__gte=date.today(),
        appointment_date__lte=date.today() + timedelta(days=7),
    ).order_by("appointment_date")[:5]

    # -------------------------------
    # Today's medicines count
    # -------------------------------
    today_medicines_count = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient__in=patients,
        is_active=True
    ).count()

    

    # -------------------------------
    # Context
    # -------------------------------
    context = {
        "links": approved_links,                 # existing usage
        "pending_links": pending_links,          # ✅ NEW (for UI)
        "rejected_links": rejected_links,
        "approved_count": approved_links.count(),
        "pending_count": pending_links.count(),
        "upcoming_appointments": upcoming_appointments,
        "today_medicines_count": today_medicines_count,
    }

    return render(request, "family/dashboard.html", context)

# ======================================================
# REQUEST DEPENDENT
# ======================================================

@role_required("family")
def request_dependent(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        relation = request.POST.get("relation", "").strip()

        user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier),
            role="patient"
        ).first()

        if not user:
            messages.error(request, "Patient does not exist.")
            return redirect("family:request_dependent")

        try:
            patient = user.patient_profile
        except PatientProfile.DoesNotExist:
            messages.error(request, "This user is not a patient.")
            return redirect("family:request_dependent")

        if user == request.user:
            messages.error(request, "You cannot add yourself as a dependent.")
            return redirect("family:request_dependent")

        link = FamilyPatientLink.objects.filter(
            family_member=request.user,
            patient=patient
        ).first()

        if link:
            if link.status == "approved":
                messages.warning(request, "Patient already linked.")
                return redirect("family:request_dependent")

            if link.status == "pending":
                messages.info(request, "Request already pending.")
                return redirect("family:request_dependent")

            if link.status == "rejected":
                link.status = "pending"
                link.is_active = False
                link.relation = relation
                link.save()
                messages.success(request, "Request sent again.")
                return redirect("family:dashboard")

        FamilyPatientLink.objects.create(
            family_member=request.user,
            patient=patient,
            relation=relation,
            status="pending",
            is_active=False
        )

        messages.success(request, "Dependent request sent.")
        return redirect("family:dashboard")

    return render(request, "family/request_dependent.html")

# ======================================================
# PATIENT READ‑ONLY VIEWS
# ======================================================

@role_required("family")
def view_patient_profile(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()
    return render(request, "family/patient_profile_readonly.html", {"patient": patient})


@role_required("family")
def view_patient_medicines(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    prescriptions = Prescription.objects.filter(
        patient=patient.user
    ).prefetch_related("items__medicine").order_by("-created_at")

    return render(
        request,
        "family/patient_medicines.html",
        {"patient": patient, "prescriptions": prescriptions}
    )


@role_required("family")
def view_patient_schedules(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    schedules = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient=patient.user,
        is_active=True
    ).select_related("prescription_item__medicine").order_by("time")

    return render(
        request,
        "family/patient_schedules.html",
        {"patient": patient, "schedules": schedules}
    )


@role_required("family")
def view_patient_documents(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    documents = MedicalDocument.objects.filter(
        patient=patient.user,
        is_active=True
    ).order_by("-uploaded_at")

    return render(
        request,
        "family/patient_documents.html",
        {"patient": patient, "documents": documents}
    )

# ======================================================
# APPOINTMENTS (FAMILY)
# ======================================================

@role_required("family")
def family_patient_appointments(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    appointments = Appointment.objects.filter(
        patient=patient.user
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "family/patient_appointments.html",
        {
            "patient": patient,
            "appointments": appointments,
            "can_manage": can_family_manage_appointments(request.user, patient),
        }
    )


@role_required("family")
def family_create_appointment(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_manage_appointments(request.user, patient):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            date_ = form.cleaned_data["appointment_date"]
            time_ = form.cleaned_data["appointment_time"]

            exists = Appointment.objects.filter(
                patient=patient.user,
                appointment_date=date_,
                appointment_time=time_,
                status__in=["requested", "approved"]
            ).exists()

            if exists:
                form.add_error(None, "Appointment already exists.")
            else:
                appt = form.save(commit=False)
                appt.patient = patient.user
                appt.status = "requested"
                appt.created_by_family = request.user
                appt.save()
                messages.success(request, "Appointment requested.")
                return redirect("family:patient_appointments", patient_id=patient.id)
    else:
        form = AppointmentRequestForm()

    return render(
        request,
        "family/create_appointment.html",
        {"form": form, "patient": patient}
    )


@role_required("family")
def family_cancel_appointment(request, patient_id, appointment_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        patient=patient.user
    )

    if appointment.status == "completed":
        return HttpResponseForbidden()

    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save(update_fields=["status"])
        return redirect("family:patient_appointments", patient_id=patient.id)

    return render(
        request,
        "family/confirm_cancel.html",
        {"appointment": appointment}
    )

# ======================================================
# PATIENT OVERVIEW
# ======================================================

@role_required("family")
def patient_overview(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden()

    context = {
        "patient": patient,
        "appointment_count": Appointment.objects.filter(patient=patient.user).count(),
        "prescription_count": Prescription.objects.filter(patient=patient.user).count(),
        "document_count": MedicalDocument.objects.filter(
            patient=patient.user,
            is_active=True
        ).count(),
    }

    return render(request, "family/patient_overview.html", context)

# ======================================================
# ADHERENCE INSIGHTS
# ======================================================

@role_required("family")
def family_adherence_insights(request):
    links = FamilyPatientLink.objects.filter(
        family_member=request.user,
        status="approved",
        is_active=True
    ).select_related("patient__user")

    patient_adherence = []
    total_taken = total_missed = risk_patients = 0
    percentages = []

    for link in links:
        stats = get_adherence_stats(link.patient.user, days=7)
        percent = stats["adherence"] or 0

        total_taken += stats["taken"]
        total_missed += stats["missed"]

        if stats["adherence"] is not None:
            percentages.append(percent)
            if percent < 50:
                risk_patients += 1

        patient_adherence.append({
            "patient_name": link.patient.user.get_full_name() or link.patient.user.username,
            "percent": percent,
        })

    overall_adherence = round(sum(percentages) / len(percentages), 1) if percentages else 0

    return render(
        request,
        "family/adherence_insights.html",
        {
            "overall_adherence": overall_adherence,
            "taken_count": total_taken,
            "missed_count": total_missed,
            "risk_patients_count": risk_patients,
            "patient_adherence": patient_adherence,
            "missed_logs": [],
        }
    )