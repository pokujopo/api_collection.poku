# main_project/celery.py
import os
from celery import Celery

# Weka settings za Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('kichaka_platform')

# Kusoma configs zote zenye herufi kubwa kule kwenye settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# UJANJA NDIO HUU: Inatafuta 'tasks.py' kwenye app zote na ma-folder yote
app.autodiscover_tasks()
