import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vianue.settings')
app = Celery('vianue')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
