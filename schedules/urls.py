from django.urls import path
from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.schedule_list, name="list"),
    path("create/", views.schedule_create, name="create"),
    path("<int:pk>/edit/", views.schedule_update, name="edit"),
    path("<int:pk>/delete/", views.schedule_delete, name="delete"),
]
