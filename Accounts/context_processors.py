from Accounts.models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': request.user.notifications.all().order_by('-timestamp')[:5]
        }
    return {}
