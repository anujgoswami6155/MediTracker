from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    
    # Auth & Core
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    
    # Patient Features
    path('patients/', include('patients.urls')),        
    path('schedules/', include('schedules.urls')),      
    path('adherence/', include('adherence.urls')),      
    path('documents/', include('documents.urls')),
    path('appointments/', include('appointments.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)