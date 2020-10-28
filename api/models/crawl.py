from django.db import models
from django.utils.translation import gettext_lazy as _

class Crawl (models.Model):
    _type = models.CharField(max_length=255)
    data = models.TextField(blank=True)
    crawl = models.BooleanField()
