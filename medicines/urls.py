from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    # Medicine Catalog
    path('', views.medicine_list, name='list'),
    path('<int:pk>/', views.medicine_detail, name='detail'),
    path('create/', views.medicine_create, name='create'),
    path('<int:pk>/edit/', views.medicine_edit, name='edit'),
    path('<int:pk>/delete/', views.medicine_delete, name='delete'),
    
    # Prescriptions
    path('prescriptions/', views.my_prescriptions, name='prescriptions'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:prescription_pk>/add-medicine/', views.add_medicine_to_prescription, name='add_medicine_to_prescription'),
]