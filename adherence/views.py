from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from .models import IntakeLog, Reminder
from .forms import IntakeLogForm, ReminderForm

PATIENT_SCHEDULE_LOOKUP = "schedule__prescription_item__prescription__patient"


# ---------------------------
# INTAKE LOGS (patient)
# ---------------------------
@role_required("patient")
def intake_list(request):
    logs = IntakeLog.objects.filter(patient=request.user).select_related("schedule").order_by("-id")
    
    # Calculate stats
    total_logs = logs.count()
    taken_count = logs.filter(status='taken').count()
    missed_count = logs.filter(status='missed').count()
    skipped_count = logs.filter(status='skipped').count()
    
    return render(request, "adherence/intake_list.html", {
        "logs": logs,
        "total_logs": total_logs,
        "taken_count": taken_count,
        "missed_count": missed_count,
        "skipped_count": skipped_count,
    })


@role_required("patient")
def intake_create(request):
    if request.method == "POST":
        form = IntakeLogForm(request.user, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.patient = request.user  # ✅ always set patient
            obj.save()
            return redirect("adherence:intake_list")
    else:
        form = IntakeLogForm(request.user)

    return render(request, "adherence/form.html", {"form": form, "title": "Add Intake Log"})


@role_required("patient")
def intake_update(request, pk):
    log = get_object_or_404(IntakeLog, pk=pk, patient=request.user)

    if request.method == "POST":
        form = IntakeLogForm(request.user, request.POST, instance=log)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.patient = request.user
            obj.save()
            return redirect("adherence:intake_list")
    else:
        form = IntakeLogForm(request.user, instance=log)

    return render(request, "adherence/form.html", {"form": form, "title": "Edit Intake Log"})


@role_required("patient")
def intake_delete(request, pk):
    log = get_object_or_404(IntakeLog, pk=pk, patient=request.user)

    if request.method == "POST":
        log.delete()
        return redirect("adherence:intake_list")

    return render(request, "adherence/delete.html", {"obj": log})


# ---------------------------
# REMINDERS (patient)
# ---------------------------
@role_required("patient")
def reminder_list(request):
    reminders = Reminder.objects.filter(
        schedule__prescription_item__prescription__patient=request.user
    ).select_related("schedule").order_by("-id")
    return render(request, "adherence/reminder_list.html", {"reminders": reminders})


@role_required("patient")
def reminder_create(request):
    if request.method == "POST":
        form = ReminderForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("adherence:reminder_list")
    else:
        form = ReminderForm(request.user)

    return render(request, "adherence/form.html", {"form": form, "title": "Add Reminder"})


@role_required("patient")
def reminder_update(request, pk):
    reminder = get_object_or_404(
        Reminder,
        pk=pk,
        schedule__prescription_item__prescription__patient=request.user
    )

    if request.method == "POST":
        form = ReminderForm(request.user, request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            return redirect("adherence:reminder_list")
    else:
        form = ReminderForm(request.user, instance=reminder)

    return render(request, "adherence/form.html", {"form": form, "title": "Edit Reminder"})


@role_required("patient")
def reminder_delete(request, pk):
    reminder = get_object_or_404(
        Reminder,
        pk=pk,
        schedule__prescription_item__prescription__patient=request.user
    )

    if request.method == "POST":
        reminder.delete()
        return redirect("adherence:reminder_list")

    return render(request, "adherence/delete.html", {"obj": reminder})
