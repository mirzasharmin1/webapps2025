from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webapps2025/', include('payapp.urls')),
    path('auth/', include('register.urls')),
    path('conversion/', include('conversion.urls')),
    path('time/', include('timestamp_service.urls')),

    path('', RedirectView.as_view(url='/auth/login')),
]
