from django.urls import path
from . import views

app_name = 'timestamp_service'

urlpatterns = [
    path('', views.test_timestamp, name='test_timestamp'),
]
