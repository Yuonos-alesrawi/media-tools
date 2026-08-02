from django.db import models
from urllib.parse import urlparse
# Create your models here.

class Jobs(models.Model):
    class JobChoices(models.TextChoices):
        mp3 = 'Mp3', 'Mp3'
        video = 'VID', 'Video'
        compress = 'CMP', 'Compress'
        cut = 'Cut', 'Cut'
    url = models.TextField()
    selected_format_id = models.CharField(max_length=100,null=True,blank=True)
    website_name = models.CharField(max_length=100,blank=True,null=True)
    job_type = models.CharField(max_length=3,choices=JobChoices)
    status = models.CharField(max_length=20,default='pending')
    filepath = models.CharField(max_length=500,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.website_name and self.url:
            self.website_name = urlparse(self.url).netloc
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.website_name)
