from django.db import models


class CurrencyPair(models.Model):
    source_currency = models.CharField(max_length=3)
    destination_currency = models.CharField(max_length=3)
    conversion_rate = models.DecimalField(max_digits=12, decimal_places=6,
                                          help_text="1 unit of source_currency = X units of destination_currency")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['source_currency', 'destination_currency']

    def __str__(self):
        return f"1 {self.source_currency} = {self.conversion_rate} {self.destination_currency}"
