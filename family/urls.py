# family/urls.py
from django.urls import path
from .views import family_dashboard

urlpatterns = [
    path("dashboard/", family_dashboard, name="family_dashboard"),
]