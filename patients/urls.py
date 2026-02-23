from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("dependent-requests/", views.dependent_requests, name="dependent_requests"),
path(
    "dependent-requests/<int:pk>/<str:action>/",
    views.respond_dependent_request,
    name="respond_dependent_request"
),
path(
    "dependent-requests/",
    views.dependent_requests,
    name="dependent_requests"
),

path(
    "dependent-requests/<int:pk>/<str:action>/",
    views.handle_dependent_request,
    name="handle_dependent_request"
),
]