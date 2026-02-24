from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.db.models import Q

from patients.models import PatientProfile
from medicines.models import Prescription
from schedules.models import MedicineSchedule

from .models import FamilyPatientLink
from .utils import is_family_member, can_family_access_patient
from core.decorators import role_required
User = get_user_model()


# ======================================================
# FAMILY DASHBOARD
# ======================================================

from datetime import date, timedelta
from appointments.models import Appointment
from schedules.models import MedicineSchedule

@login_required
def family_dashboard(request):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    links = FamilyPatientLink.objects.filter(
        family_member=request.user,
        status="approved",
        is_active=True
    ).select_related("patient__user")

    patients = [link.patient for link in links]

    upcoming_appointments = Appointment.objects.filter(
        patient__in=[p.user for p in patients],
        appointment_date__gte=date.today(),
        appointment_date__lte=date.today() + timedelta(days=7)
    ).order_by("appointment_date")[:5]

    today_medicines_count = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient__in=[p.user for p in patients],
        is_active=True
    ).count()

    context = {
        "links": links,
        "approved_count": links.count(),
        "pending_count": FamilyPatientLink.objects.filter(
            family_member=request.user, status="pending"
        ).count(),
        "upcoming_appointments": upcoming_appointments,
        "today_medicines_count": today_medicines_count,
    }

    return render(request, "family/dashboard.html", context)


# ======================================================
# REQUEST DEPENDENT
# ======================================================

@login_required
def request_dependent(request):
    if not is_family_member(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect("family:dashboard")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        relation = request.POST.get("relation", "").strip()

        # 1️⃣ Find patient user
        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier),
            role="patient"
        ).first()

        if not user:
            messages.error(
                request,
                "Patient with this username or email does not exist."
            )
            return redirect("family:request_dependent")

        # 2️⃣ Get PatientProfile
        try:
            patient = user.patient_profile
        except PatientProfile.DoesNotExist:
            messages.error(request, "This user is not a patient.")
            return redirect("family:request_dependent")

        # 3️⃣ Prevent self‑linking
        if user == request.user:
            messages.error(request, "You cannot add yourself as a dependent.")
            return redirect("family:request_dependent")

        # 4️⃣ Existing link check
        existing_link = FamilyPatientLink.objects.filter(
            family_member=request.user,
            patient=patient
        ).first()

        if existing_link:
            if existing_link.status == "approved":
                messages.warning(
                    request,
                    "This patient is already linked to your account."
                )
                return redirect("family:request_dependent")

            if existing_link.status == "pending":
                messages.info(
                    request,
                    "A request for this patient is already pending approval."
                )
                return redirect("family:request_dependent")

            # 🔁 Re‑request after rejection
            if existing_link.status == "rejected":
                existing_link.status = "pending"
                existing_link.is_active = False
                existing_link.relation = relation
                existing_link.save(
                    update_fields=["status", "is_active", "relation"]
                )

                messages.success(
                    request,
                    "Previous request was rejected. A new request has been sent."
                )
                return redirect("family:dashboard")

        # 5️⃣ Create new request
        FamilyPatientLink.objects.create(
            family_member=request.user,
            patient=patient,
            relation=relation,
            status="pending",
            is_active=False
        )

        messages.success(
            request,
            "Dependent request sent successfully. Waiting for patient approval."
        )
        return redirect("family:dashboard")

    return render(request, "family/request_dependent.html")


# ======================================================
# STEP 6.2 — VIEW PATIENT PROFILE (READ‑ONLY)
# ======================================================

@login_required
def view_patient_profile(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    return render(
        request,
        "family/patient_profile_readonly.html",
        {"patient": patient}
    )


# ======================================================
# STEP 6.3 — VIEW PATIENT MEDICINES (READ‑ONLY)
# ======================================================

@login_required
def view_patient_medicines(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    prescriptions = Prescription.objects.filter(
        patient=patient.user
    ).prefetch_related("items__medicine").order_by("-created_at")

    return render(
        request,
        "family/patient_medicines.html",
        {
            "patient": patient,
            "prescriptions": prescriptions,
        }
    )


# ======================================================
# STEP 6.4 — VIEW PATIENT MEDICINE SCHEDULES (READ‑ONLY)
# ======================================================

@login_required
def view_patient_schedules(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    schedules = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient=patient.user,
        is_active=True
    ).select_related(
        "prescription_item__medicine"
    ).order_by("time")

    return render(
        request,
        "family/patient_schedules.html",
        {
            "patient": patient,
            "schedules": schedules,
        }
    )

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponseForbidden

from documents.models import MedicalDocument
# from patients.models import PatientProfile
from .utils import can_family_manage_appointments

@login_required
def view_patient_documents(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    patient = get_object_or_404(PatientProfile, pk=patient_id)

    # 🔐 Access check
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    documents = MedicalDocument.objects.filter(
        patient=patient.user,
        is_active=True
    ).order_by("-uploaded_at")

    return render(
        request,
        "family/patient_documents.html",
        {
            "patient": patient,
            "documents": documents
        }
    )


# family/views.py
from appointments.models import Appointment

@login_required
def family_patient_appointments(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

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
            "can_manage": can_family_manage_appointments(
                request.user, patient
            ),
        }
    )
from appointments.forms import AppointmentRequestForm

@login_required
def family_create_appointment(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if not can_family_manage_appointments(request.user, patient):
        return HttpResponseForbidden("You cannot create appointments for this patient")

    if request.method == "POST":
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment_date = form.cleaned_data["appointment_date"]
            appointment_time = form.cleaned_data["appointment_time"]

            # ✅ DUPLICATE CHECK (CORE FIX)
            exists = Appointment.objects.filter(
                patient=patient.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=["requested", "approved"]
            ).exists()

            if exists:
             form.add_error(
              None,
              "An appointment already exists for this date and time."
            )
             return render(
              request,
        "family/create_appointment.html",
        {
            "form": form,
            "patient": patient,
        }
    )

            appointment = form.save(commit=False)
            appointment.patient = patient.user
            appointment.status = "requested"
            appointment.created_by_family = request.user
            appointment.save()

            messages.success(request, "Appointment requested successfully.")
            return redirect(
                "family:patient_appointments",
                patient_id=patient.id
            )
    else:
        form = AppointmentRequestForm()

    return render(
        request,
        "family/create_appointment.html",
        {
            "form": form,
            "patient": patient,
        }
    )
@role_required("family")
@login_required
def family_cancel_appointment(request, patient_id, appointment_id):

    # 1️⃣ Get patient
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    # 2️⃣ Permission check
    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    # 3️⃣ Get appointment (must belong to patient)
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        patient=patient.user
    )

    # 4️⃣ Safety rule
    if appointment.status == "completed":
        return HttpResponseForbidden("Completed appointments cannot be cancelled")

    # 5️⃣ Cancel on POST
    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save(update_fields=["status"])
        return redirect(
            "family:patient_appointments",
            patient_id=patient.id
        )

    # 6️⃣ Confirmation page
    return render(
        request,
        "family/confirm_cancel.html",
        {"appointment": appointment}
    )


from medicines.models import Prescription
from documents.models import MedicalDocument
from appointments.models import Appointment

@login_required
def patient_overview(request, patient_id):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if not can_family_access_patient(request.user, patient):
        return HttpResponseForbidden("Access denied")

    from appointments.models import Appointment
    from medicines.models import Prescription
    from documents.models import MedicalDocument

    context = {
        "patient": patient,
        "appointment_count": Appointment.objects.filter(
            patient=patient.user
        ).count(),

        "prescription_count": Prescription.objects.filter(
            patient=patient.user
        ).count(),

        "document_count": MedicalDocument.objects.filter(
            patient=patient.user,
            is_active=True
        ).count(),
    }

    return render(
        request,
        "family/patient_overview.html",
        context
    )