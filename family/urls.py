from django.urls import path
from .views import family_dashboard, request_dependent

app_name = "family"

urlpatterns = [
    path("dashboard/", family_dashboard, name="dashboard"),
    path("request-dependent/", request_dependent, name="request_dependent"),
]