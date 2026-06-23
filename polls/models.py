#from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

#from django.db import models

class Test(models.Model):
    # Machaguzi ya format
    FORMAT_CHOICES = [
        ('video', 'Video (MP4)'),
        ('audio', 'Audio (MP3)'),
    ]
    
    # Machaguzi ya ubora wa picha
    QUALITY_CHOICES = [
        ('360p', '360p (Low)'),
        ('720p', '720p (HD)'),
        ('1080p', '1080p (Full HD)'),
        ('best', 'Best Quality'),
    ]

    link = models.URLField(max_length=1000)
    name = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    error_message = models.TextField(blank=True, null=True)
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='video')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='720p')
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.status}"

"""
class Test(models.Model):
    # null=True na blank=True inaruhusu data kusaviwa kupitia API Bila kulazimisha login ya mtu
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, default="Video_Iliyopakuliwa")
    link = models.URLField()
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.link}"
"""