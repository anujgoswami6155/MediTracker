from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_role is None:
            return redirect("accounts:login")

        if request.user.role != self.required_role:
            return redirect("accounts:login")

        return super().dispatch(request, *args, **kwargs)


class PatientOnlyMixin(RoleRequiredMixin):
    required_role = "patient"


class DoctorOnlyMixin(RoleRequiredMixin):
    required_role = "doctor"


class FamilyOnlyMixin(RoleRequiredMixin):
    required_role = "family"
