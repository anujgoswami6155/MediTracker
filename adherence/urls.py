from django.urls import path
from . import views

app_name = "adherence"

urlpatterns = [
    # intake logs
    path("intake/", views.intake_list, name="intake_list"),
    path("intake/create/", views.intake_create, name="intake_create"),
    path("intake/<int:pk>/edit/", views.intake_update, name="intake_edit"),
    path("intake/<int:pk>/delete/", views.intake_delete, name="intake_delete"),

    # reminders
    path("reminders/", views.reminder_list, name="reminder_list"),
    path("reminders/create/", views.reminder_create, name="reminder_create"),
    path("reminders/<int:pk>/edit/", views.reminder_update, name="reminder_edit"),
    path("reminders/<int:pk>/delete/", views.reminder_delete, name="reminder_delete"),
]
