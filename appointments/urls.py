from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
   
    path("patient/", views.patient_appointments, name="patient_list"),
    path("patient/request/", views.request_appointment, name="request"),
    path("patient/<int:pk>/cancel/", views.cancel_appointment, name="cancel"),

  
    path("doctor/", views.doctor_appointments, name="doctor_list"),
    path("doctor/<int:pk>/edit/", views.update_appointment, name="doctor_edit"),
    path("doctor/<int:pk>/review/", views.review_appointment, name="doctor_review"),
    path("doctor/<int:pk>/details/", views.appointment_details, name="doctor_details"),
    path("doctor/<int:pk>/reschedule/", views.reschedule_appointment, name="doctor_reschedule"),
]