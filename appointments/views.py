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
    today = timezone.localdate()
    seven_days_ago = today - timedelta(days=7)

    appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__gte=seven_days_ago
    ).order_by(
        "-appointment_date",
        "-appointment_time"
    )

    # ✅ Missed Count
    missed_count = Appointment.objects.filter(
        doctor=request.user,
        status="requested",
        appointment_date__lt=today
    ).count()

    return render(
        request,
        "doctor/appointment_list.html",
        {
            "appointments": appointments,
            "today": today,
            "missed_count": missed_count,  # 🔥 send to template
        }
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
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from core.decorators import role_required
from .models import Appointment


@role_required("doctor")
def review_appointment(request, pk):
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        doctor=request.user
    )

    today = timezone.localdate()

    # Allow modify ONLY on exact appointment date AND approved
    can_modify = (
        appt.appointment_date == today and
        appt.status == "approved"
    )

    # ✅ FIXED HISTORY QUERY
    history = Appointment.objects.filter(
        patient=appt.patient,
        status__in=["approved", "completed"],
        appointment_date__lt=appt.appointment_date
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

        action = request.POST.get("action")
        notes = request.POST.get("doctor_notes")
        follow_up = request.POST.get("follow_up_date")

        # Restrict notes + complete
        if action == "complete" or (notes and notes.strip() != ""):
            if not can_modify:
                messages.error(
                    request,
                    "Notes and completion are only allowed on the appointment date after approval."
                )
                return redirect("appointments:doctor_review", pk=appt.pk)

        # Save notes
        if notes is not None and can_modify:
            appt.doctor_notes = notes

        # Save follow-up date
        if follow_up and can_modify:
            follow_up_date_obj = datetime.strptime(
                follow_up, "%Y-%m-%d"
            ).date()

            appt.follow_up_date = follow_up_date_obj

            # ✅ AUTO COPY NOTES TO FOLLOW-UP APPOINTMENT
            if notes and notes.strip() != "":
                next_appt = Appointment.objects.filter(
                    patient=appt.patient,
                    appointment_date=follow_up_date_obj
                ).exclude(
                    pk=appt.pk
                ).first()

                if next_appt:
                    next_appt.doctor_notes = notes
                    next_appt.save(update_fields=["doctor_notes"])

        elif can_modify:
            appt.follow_up_date = None

        # Actions
        if action == "approve":
            appt.status = "approved"

        elif action == "complete" and can_modify:
            appt.status = "completed"

        elif action == "reschedule":
            return redirect("appointments:doctor_reschedule", pk=appt.pk)

        appt.save()

        messages.success(request, "Appointment updated successfully.")
        return redirect("appointments:doctor_list")

    
    previous_followup = Appointment.objects.filter(
        patient=appt.patient,
        follow_up_date=appt.appointment_date,
        status="completed"
    ).exclude(
        pk=appt.pk
    ).order_by("-appointment_date").first()

    return render(
        request,
        "doctor/appointment_review.html",
        {
            "appointment": appt,
            "history": history,
            "documents": documents,
            "can_modify": can_modify,
            "previous_followup": previous_followup,   
            "today": today,
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

    # 🚫 BLOCK IF APPOINTMENT DATE IS ALREADY GONE
    if appt.appointment_date < today:
        messages.error(request, "Past appointments cannot be rescheduled.")
        return redirect("appointments:doctor_list")

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