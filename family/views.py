from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import FamilyPatientLink
from .utils import is_family_member

@login_required
def family_dashboard(request):
    if not is_family_member(request.user):
        return render(request, "403.html")

    dependents = FamilyPatientLink.objects.filter(
        family_member=request.user,
        is_active=True
    ).select_related("patient__user")

    return render(
        request,
        "family/dashboard.html",
        {"dependents": dependents}
    )