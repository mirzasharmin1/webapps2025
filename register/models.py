from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from timestamp_service.client import get_timestamp
from conversion.models import CurrencyPair


class Account(models.Model):
    CURRENCY_CHOICES = [
        ('GBP', 'GB Pounds (£)'),
        ('USD', 'US Dollars ($)'),
        ('EUR', 'Euros (€)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.CharField(max_length=30, blank=True, null=True)

    @classmethod
    def get_all_accounts(cls):
        """Return all accounts with related user info"""
        return cls.objects.select_related('user').all()

    @property
    def user_full_name(self):
        """Returns the user's full name or username if not available"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

    def __str__(self):
        return f"{self.user.username}'s Account ({self.currency})"


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    """Create an account for new users with initial balance in their chosen currency"""
    if created:
        timestamp = get_timestamp()
        if not timestamp:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        Account.objects.create(user=instance, created_at=timestamp)


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()
