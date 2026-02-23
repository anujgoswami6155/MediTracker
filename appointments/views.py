from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from .models import Appointment
from .forms import AppointmentRequestForm, AppointmentDoctorUpdateForm
from django.utils import timezone
from datetime import timedelta




# =====================================================
# PATIENT SECTION
# =====================================================

@role_required("patient")
def patient_appointments(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by("-created_at")

    return render(
        request,
        "appointments/patient_list.html",
        {"appointments": appointments}
    )


@role_required("patient")
def request_appointment(request):
    if request.method == "POST":
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user
            appt.status = "requested"
            appt.save()
            return redirect("appointments:patient_list")
    else:
        form = AppointmentRequestForm()

    return render(
        request,
        "appointments/form.html",
        {"form": form, "title": "Request Appointment"}
    )


@role_required("patient")
def cancel_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        patient=request.user
    )

    if appt.status == "completed":
        return redirect("appointments:patient_list")

    if request.method == "POST":
        appt.status = "cancelled"
        appt.save(update_fields=["status"])
        return redirect("appointments:patient_list")

    return render(
        request,
        "appointments/confirm.html",
        {
            "title": "Cancel Appointment",
            "obj": appt
        }
    )


# =====================================================
# DOCTOR SECTION
# =====================================================

@role_required("doctor")
def doctor_appointments(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__gte=seven_days_ago
    ).order_by(
        "-appointment_date",
        "-appointment_time"
    )

    return render(
        request,
        "doctor/appointment_list.html",
        {"appointments": appointments}
    )


@role_required("doctor")
def update_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    if request.method == "POST":
        form = AppointmentDoctorUpdateForm(
            request.POST,
            instance=appt
        )
        if form.is_valid():
            form.save()
            return redirect("appointments:doctor_list")
    else:
        form = AppointmentDoctorUpdateForm(instance=appt)

    return render(
        request,
        "appointments/form.html",
        {"form": form, "title": "Update Appointment"}
    )


# =====================================================
# REVIEW APPOINTMENT (UPDATED WITH HISTORY + DOCS + INSTRUCTIONS)
# =====================================================

@role_required("doctor")
def review_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    # ✅ Medical History (ONLY previous approved visits)
    history = Appointment.objects.filter(
        patient=appt.patient,
        status="approved",
        appointment_date__lt=appt.appointment_date
    ).order_by("-appointment_date")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            appt.status = "approved"
            appt.save(update_fields=["status"])
            return redirect("appointments:doctor_list")

        if action == "reschedule":
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

    return render(
        request,
        "doctor/appointment_review.html",
        {
            "appointment": appt,
            "history": history,
        }
    )


@role_required("doctor")
def appointment_details(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    return render(
        request,
        "doctor/appointment_details.html",
        {"appointment": appt}
    )


@role_required("doctor")
def reschedule_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    if request.method == "POST":
        new_date = request.POST.get("appointment_date")
        new_time = request.POST.get("appointment_time")

        if new_date and new_time:
            appt.appointment_date = new_date
            appt.appointment_time = new_time
            appt.status = "approved"
            appt.save(update_fields=[
                "appointment_date",
                "appointment_time",
                "status"
            ])
            return redirect("appointments:doctor_list")

    return render(
        request,
        "doctor/reschedule_appointment.html",
        {"appointment": appt}
    )