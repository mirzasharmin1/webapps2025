from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('', views.home, name='home'),

    # Money transfer
    path('send-money/', views.send_money, name='send_money'),
    path('request-money/', views.request_money, name='request_money'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),




    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_accounts, name='admin_user_accounts'),
    path('admin/users/toggle-staff/<int:user_id>/', views.admin_toggle_staff_status, name='admin_toggle_staff'),
    path('admin/create-admin/', views.admin_create_admin, name='admin_create_admin'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
]
