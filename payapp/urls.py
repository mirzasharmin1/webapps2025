from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_placeholder, name='dashboard'),
]
