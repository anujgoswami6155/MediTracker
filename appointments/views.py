from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from .models import Appointment
from .forms import AppointmentRequestForm, AppointmentDoctorUpdateForm


# -------------------
# PATIENT
# -------------------
@role_required("patient")
def patient_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by("-created_at")
    return render(request, "appointments/patient_list.html", {"appointments": appointments})


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

    return render(request, "appointments/form.html", {"form": form, "title": "Request Appointment"})


@role_required("patient")
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)

    # only allow cancel if not completed
    if appt.status == "completed":
        return redirect("appointments:patient_list")

    if request.method == "POST":
        appt.status = "cancelled"
        appt.save(update_fields=["status"])
        return redirect("appointments:patient_list")

    return render(request, "appointments/confirm.html", {
        "title": "Cancel Appointment",
        "obj": appt
    })


# -------------------
# DOCTOR
# -------------------
@role_required("doctor")
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user).order_by("-created_at")
    return render(request, "appointments/doctor_list.html", {"appointments": appointments})


@role_required("doctor")
def update_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)

    if request.method == "POST":
        form = AppointmentDoctorUpdateForm(request.POST, instance=appt)
        if form.is_valid():
            form.save()
            return redirect("appointments:doctor_list")
    else:
        form = AppointmentDoctorUpdateForm(instance=appt)

    return render(request, "appointments/form.html", {"form": form, "title": "Update Appointment"})
