from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('currency',)
