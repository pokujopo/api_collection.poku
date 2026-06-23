# jina_la_project_yako/celery.py
import os
from celery import Celery

# Set default Django settings module kwa ajili ya celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Tengeneza instance ya Celery (Upe jina mradi wako)
app = Celery('myproject')

# Soma config zote za celery kutoka kwenye settings.py
# Neno 'CELERY' linamaanisha config zote zianze na neno hilo (mfano: CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# ──── HAPA NDIO MIUJIZA ILIPO ────
# Hii inamwambia Celery apitie kila app na agundue ma-faili ya 'tasks.py' kiotomatiki!
app.autodiscover_tasks()

