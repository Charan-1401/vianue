from celery import shared_task
from django.utils import timezone
from .models import Hold


@shared_task
def cleanup_expired_holds():
    now = timezone.now()
    expired = Hold.objects.filter(expires_at__lt=now)
    count = expired.count()
    expired.delete()
    return {'deleted': count}
