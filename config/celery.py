import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('fretehub')

# Configure Celery with Django settings namespace CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all registered Django apps
app.autodiscover_tasks()
