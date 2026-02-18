from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("upload/", views.upload_document, name="upload"),
    path("<int:pk>/", views.document_detail, name="detail"),
    path("<int:pk>/delete/", views.delete_document, name="delete"),
]
