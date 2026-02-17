from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from .models import MedicineSchedule
from .forms import MedicineScheduleForm


@role_required("patient")
def schedule_list(request):
    schedules = MedicineSchedule.objects.filter(
        prescription_item__prescription__patient=request.user
    ).select_related("prescription_item").order_by("-id")

    return render(request, "schedules/list.html", {"schedules": schedules})


@role_required("patient")
def schedule_create(request):
    if request.method == "POST":
        form = MedicineScheduleForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedules:list")
    else:
        form = MedicineScheduleForm(request.user)

    return render(request, "schedules/form.html", {
        "form": form,
        "title": "Create Schedule"
    })


@role_required("patient")
def schedule_update(request, pk):
    schedule = get_object_or_404(
        MedicineSchedule,
        pk=pk,
        prescription_item__prescription__patient=request.user
    )

    if request.method == "POST":
        form = MedicineScheduleForm(request.user, request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("schedules:list")
    else:
        form = MedicineScheduleForm(request.user, instance=schedule)

    return render(request, "schedules/form.html", {
        "form": form,
        "title": "Update Schedule"
    })


@role_required("patient")
def schedule_delete(request, pk):
    schedule = get_object_or_404(
        MedicineSchedule,
        pk=pk,
        prescription_item__prescription__patient=request.user
    )

    if request.method == "POST":
        schedule.delete()
        return redirect("schedules:list")

    return render(request, "schedules/delete.html", {"schedule": schedule})
