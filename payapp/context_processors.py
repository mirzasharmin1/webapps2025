from .models import Notification


def notification_processor(request):
    context_data = {'notifications_unread_count': 0}

    if request.user.is_authenticated:
        notifications_unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        context_data['notifications_unread_count'] = notifications_unread_count

    return context_data
