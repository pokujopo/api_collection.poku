# plugins/media_downloader/models.py
from django.db import models
import uuid

class DownloadedMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500)
    status = models.CharField(max_length=20, default='pending') # pending, completed, failed, deleted
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kichaka_downloaded_media' # Inalazimisha jina la table bila kujali INSTALLED_APPS
