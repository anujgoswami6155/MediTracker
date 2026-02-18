from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='accounts/login/')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')), 
    path("appointments/", include("appointments.urls")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
