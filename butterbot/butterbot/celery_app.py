from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from celery import Celery
import os
import django
# set the default Django settings module for the 'celery' program.
#from settings import TIME_ZONE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'butterbot.settings')
django.setup()
app = Celery('butterbot')


#CELERY_TIMEZONE = TIME_ZONE
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()




@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


if __name__ == '__main__':
    app.start()