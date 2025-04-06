from django.db import models
from django.contrib.auth.models import User
from register.models import Account
from django.db.models.signals import post_save
from django.dispatch import receiver
from timestamp_service.client import get_timestamp
from django.utils import timezone


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('PAYMENT', 'Payment'),
        ('REQUEST', 'Payment Request'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELED', 'Canceled'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_currency = models.CharField(max_length=3)
    recipient_currency = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.CharField(max_length=30)
    completed_at = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_transaction_type_display()} from {self.sender.username} to {self.recipient.username} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.timestamp:
            timestamp = get_timestamp()
            if not timestamp:
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.timestamp = timestamp

        if self.status == 'COMPLETED' and not self.completed_at:
            completed_timestamp = get_timestamp()
            if not completed_timestamp:
                completed_timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.completed_at = completed_timestamp

        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('PAYMENT_SENT', 'Payment Sent'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('REQUEST_SENT', 'Payment Request Sent'),
        ('REQUEST_RECEIVED', 'Payment Request Received'),
        ('REQUEST_ACCEPTED', 'Payment Request Accepted'),
        ('REQUEST_REJECTED', 'Payment Request Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='transaction')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    timestamp = models.CharField(max_length=30)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.timestamp:
            timestamp = get_timestamp()
            if not timestamp:
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.timestamp = timestamp
        super().save(*args, **kwargs)


@receiver(post_save, sender=Transaction)
def create_notification(sender, instance, created, **kwargs):
    """Create notifications for transaction participants"""
    if created:
        if instance.transaction_type == 'PAYMENT':
            Notification.objects.create(
                user=instance.sender,
                transaction=instance,
                notification_type='PAYMENT_SENT'
            )
            Notification.objects.create(
                user=instance.recipient,
                transaction=instance,
                notification_type='PAYMENT_RECEIVED'
            )
        elif instance.transaction_type == 'REQUEST':
            Notification.objects.create(
                user=instance.sender,
                transaction=instance,
                notification_type='REQUEST_SENT'
            )
            Notification.objects.create(
                user=instance.recipient,
                transaction=instance,
                notification_type='REQUEST_RECEIVED'
            )
    else:
        if instance.transaction_type == 'REQUEST':
            if instance.status == 'COMPLETED':
                Notification.objects.create(
                    user=instance.sender,
                    transaction=instance,
                    notification_type='REQUEST_ACCEPTED'
                )
            elif instance.status == 'REJECTED':
                Notification.objects.create(
                    user=instance.sender,
                    transaction=instance,
                    notification_type='REQUEST_REJECTED'
                )
