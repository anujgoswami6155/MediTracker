# family/utils.py
from .models import FamilyPatientLink

def is_family_member(user):
    return user.is_authenticated and user.role == "family"

def family_has_access(user, patient):
    return FamilyPatientLink.objects.filter(
        family_member=user,
        patient=patient,
        is_active=True
    ).exists()

def can_family_access_patient(family_user, patient_profile):
    return FamilyPatientLink.objects.filter(
        family_member=family_user,
        patient=patient_profile,
        status="approved",
        is_active=True
    ).exists()

def can_family_manage_appointments(family_user, patient_profile):
    return FamilyPatientLink.objects.filter(
        family_member=family_user,
        patient=patient_profile,
        status="approved",
        is_active=True
    ).exists()