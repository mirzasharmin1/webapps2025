from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'register'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),  # This has namespace 'register:login'
    path('logout/', LogoutView.as_view(next_page='register:login'), name='logout'),
]
