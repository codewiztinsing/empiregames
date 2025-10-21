# Celery configuration for Liyu Bingo
# app/core/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat configuration
app.conf.beat_schedule = {
    'cleanup-old-games': {
        'task': 'tasks.cleanup_old_games',
        'schedule': 3600.0,  # Every hour
    },
    'send-daily-stats': {
        'task': 'tasks.send_daily_stats',
        'schedule': 86400.0,  # Daily
    },
    'backup-database': {
        'task': 'tasks.backup_database',
        'schedule': 604800.0,  # Weekly
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
