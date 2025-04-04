from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('', views.home, name='home'),

    # Money transfer
    path('send-money/', views.send_money_placeholder, name='send_money'),
    path('request-money/', views.request_money_placeholder, name='request_money'),
    path('transactions/', views.transactions_placeholder, name='transactions'),
    path('profile/', views.profile_placeholder, name='profile'),
    path('notifications/', views.notifications_placeholder, name='notifications'),

    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_accounts, name='admin_user_accounts'),
    path('admin/users/toggle-staff/<int:user_id>/', views.admin_toggle_staff_status, name='admin_toggle_staff'),
    path('admin/create-admin/', views.admin_create_admin, name='admin_create_admin'),
]
