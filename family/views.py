from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.db.models import Q

from patients.models import PatientProfile
from .models import FamilyPatientLink
from .utils import is_family_member

User = get_user_model()


@login_required
def family_dashboard(request):
    if not is_family_member(request.user):
        return HttpResponseForbidden()

    links = FamilyPatientLink.objects.filter(
        family_member=request.user
    ).select_related("patient__user")

    context = {
        "links": links,
        "approved_count": links.filter(status="approved", is_active=True).count(),
        "pending_count": links.filter(status="pending").count(),
    }

    return render(request, "family/dashboard.html", context)


@login_required
def request_dependent(request):

    if not is_family_member(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect("family:dashboard")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        relation = request.POST.get("relation", "").strip()

        # 1️⃣ Find patient user by username OR email
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

        # 4️⃣ Check existing link
        existing_link = FamilyPatientLink.objects.filter(
            family_member=request.user,
            patient=patient
        ).first()

        if existing_link:

            # ✅ Already approved → block
            if existing_link.status == "approved":
                messages.warning(
                    request,
                    "This patient is already linked to your account."
                )
                return redirect("family:request_dependent")

            # ⏳ Pending → block
            if existing_link.status == "pending":
                messages.info(
                    request,
                    "A request for this patient is already pending approval."
                )
                return redirect("family:request_dependent")

            # 🔁 Rejected → ALLOW re‑request
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
                return redirect("family:request_dependent")

        # 5️⃣ Create brand‑new request
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