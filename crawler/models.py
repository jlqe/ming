from django.db import models

# Create your models here.
class Configuration(models.Model):
	lastblock = models.IntegerField(default=0)
	running = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now=True, blank=True)