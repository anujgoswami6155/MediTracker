from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("family/dashboard/", views.family_dashboard, name="family_dashboard"),
]