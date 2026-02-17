from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    # patient
    path("patient/", views.patient_appointments, name="patient_list"),
    path("patient/request/", views.request_appointment, name="request"),
    path("patient/<int:pk>/cancel/", views.cancel_appointment, name="cancel"),

    # doctor
    path("doctor/", views.doctor_appointments, name="doctor_list"),
    path("doctor/<int:pk>/edit/", views.update_appointment, name="doctor_edit"),
]
