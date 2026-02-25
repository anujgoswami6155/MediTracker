from django.urls import path
from . import views

app_name = "family"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.family_dashboard, name="dashboard"),

    # Request dependent
    path("request-dependent/", views.request_dependent, name="request_dependent"),

    #  Read-only patient profile
    path(
        "patient/<int:patient_id>/profile/",
        views.view_patient_profile,
        name="view_patient_profile"
    ),

    # Read-only medicines
    path(
        "patient/<int:patient_id>/medicines/",
        views.view_patient_medicines,
        name="view_patient_medicines"
    ),

    #  Read-only schedules
    path(
        "patient/<int:patient_id>/schedules/",
        views.view_patient_schedules,
        name="view_patient_schedules"
    ),

   path(
    "patient/<int:patient_id>/documents/",
    views.view_patient_documents,
    name="view_patient_documents"
),

path(
    "patient/<int:patient_id>/appointments/",
    views.family_patient_appointments,
    name="patient_appointments"
),
 path(
        "patient/<int:patient_id>/appointments/<int:appointment_id>/cancel/",
        views.family_cancel_appointment,
        name="cancel_appointment"   
    ),
path(
    "patient/<int:patient_id>/overview/",
    views.patient_overview,
    name="patient_overview"
),
path(
    "patient/<int:patient_id>/appointments/create/",
    views.family_create_appointment,
    name="create_appointment",
),
path("insights/", views.family_adherence_insights, name="adherence_insights"),
]