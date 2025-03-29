from django.urls import path
from . import views

app_name = 'conversion'

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount>/',
         views.currency_conversion,
         name='currency_conversion'),
]