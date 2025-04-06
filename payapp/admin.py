from django.contrib import admin
from .models import Transaction, Notification


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'sender', 'recipient', 'amount', 'sender_currency', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status', 'sender_currency')
    search_fields = ('sender__username', 'recipient__username', 'description')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'transaction', 'is_read', 'timestamp')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username',)