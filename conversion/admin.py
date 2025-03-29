from django.contrib import admin
from .models import CurrencyPair

@admin.register(CurrencyPair)
class CurrencyPairAdmin(admin.ModelAdmin):
    list_display = ('source_currency', 'destination_currency', 'conversion_rate', 'last_updated')
    search_fields = ('source_currency', 'destination_currency')
    list_filter = ('source_currency', 'destination_currency')
