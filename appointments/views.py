from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentRequestForm, AppointmentDoctorUpdateForm
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from datetime import datetime, time





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




from datetime import datetime

@role_required("doctor")
def review_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    now = timezone.now()

    # Combine appointment date + time
    appointment_datetime = datetime.combine(
        appt.appointment_date,
        appt.appointment_time
    )
    appointment_datetime = timezone.make_aware(appointment_datetime)

    # Check if appointment is past but still approved
    is_past_approved = (
        appt.status == "approved" and
        appointment_datetime < now
    )

    # Medical history
    history = Appointment.objects.filter(
        patient=appt.patient,
        status="approved",
        appointment_date__lt=now.date()
    ).exclude(
        pk=appt.pk
    ).order_by(
        "-appointment_date",
        "-appointment_time"
    )

    from documents.models import MedicalDocument

    documents = MedicalDocument.objects.filter(
        patient=appt.patient,
        is_active=True
    ).order_by("-uploaded_at")

    # ================= POST LOGIC =================
    if request.method == "POST":

        # ❌ Do not allow modification if completed
        if appt.status == "completed":
            return redirect("appointments:doctor_list")

        action = request.POST.get("action")
        notes = request.POST.get("doctor_notes")
        follow_up = request.POST.get("follow_up_date")

        # Save doctor notes
        if notes is not None:
            appt.doctor_notes = notes

        # Save follow-up date safely
        if follow_up:
            appt.follow_up_date = datetime.strptime(
                follow_up, "%Y-%m-%d"
            ).date()
        else:
            appt.follow_up_date = None

        # Handle actions
        if action == "approve":
            appt.status = "approved"

        elif action == "complete":
            appt.status = "completed"

        elif action == "reschedule":
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        appt.save()

        messages.success(request, "Appointment updated successfully.")
        return redirect("appointments:doctor_list")

    return render(
        request,
        "doctor/appointment_review.html",
        {
            "appointment": appt,
            "history": history,
            "documents": documents,
            "is_past_approved": is_past_approved,
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

    today = timezone.localdate()

    if request.method == "POST":
        new_date = request.POST.get("appointment_date")
        new_time = request.POST.get("appointment_time")

        # ---------------- DATE VALIDATION ----------------
        if not new_date:
            messages.error(request, "Please select a date.")
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()

        if new_date_obj < today:
            messages.error(request, "You cannot select a past date.")
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        # ---------------- TIME VALIDATION ----------------
        if not new_time:
            messages.error(request, "Please select a time.")
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        hour, minute = map(int, new_time.split(":"))
        selected_time = time(hour, minute)

        if selected_time < time(7, 0) or selected_time > time(20, 0):
            messages.error(request, "Time must be between 7:00 AM and 8:00 PM.")
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        if minute not in [0, 15, 30, 45]:
            messages.error(request, "Time must be in 15 minute intervals.")
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        # ---------------- SAVE ----------------
        appt.appointment_date = new_date_obj
        appt.appointment_time = selected_time
        appt.status = "approved"

        appt.save(update_fields=[
            "appointment_date",
            "appointment_time",
            "status"
        ])

        messages.success(request, "Appointment rescheduled successfully.")
        return redirect("appointments:doctor_list")

    return render(
        request,
        "doctor/reschedule_appointment.html",
        {
            "appointment": appt,
            "today": today,
        }
    )