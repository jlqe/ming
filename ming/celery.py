from __future__ import absolute_import

import os

from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ming.settings')

from django.conf import settings  # noqa

app = Celery('ming', backend=settings.CELERY_RESULT_BACKEND, broker=settings.BROKER_URL)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
