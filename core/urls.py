from django.urls import path
from core import views as core_views
from family.views import family_dashboard   # 👈 IMPORT CORRECT VIEW

app_name = "core"

urlpatterns = [
    path("patient/dashboard/", core_views.patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", core_views.doctor_dashboard, name="doctor_dashboard"),
    path("family/dashboard/", family_dashboard, name="family_dashboard"),
]