from django.db import models
from django.utils.translation import gettext_lazy as _

class Epoch (models.Model):
    epoch = models.IntegerField(default=0, blank=False, db_index=True)
    startBlock = models.IntegerField(default=0, blank=False)
    endBlock = models.IntegerField(default=0, blank=False)
    startTime = models.DateTimeField()
    endTime= models.DateTimeField()
    duration = models.IntegerField(default=0, blank=False)
    masterNodeNumber = models.IntegerField(default=0, blank=False)
    voterNumber = models.IntegerField(default=0, blank=False)
    slashedNode = models.TextField(blank=True)
    isActive = models.BooleanField(default=True)

class EpochSign (models.Model):
    epoch = models.IntegerField(default=0, db_index=True)
    validator = models.CharField(max_length=255, blank=False, db_index=True)
    signNumber = models.IntegerField(default=0, blank=False)

class Reward (models.Model):
    epoch = models.IntegerField(default=0, db_index=True)
    startBlock = models.IntegerField(default=0, blank=False)
    endBlock = models.IntegerField(default=0, blank=False)
    address = models.CharField(max_length=255, blank=False, db_index=True)
    validator = models.CharField(max_length=255, blank=False, db_index=True)
    validatorName = models.CharField(max_length=255, blank=False)
    reason = models.CharField(max_length=255, blank=False, db_index=True)
    lockBalance = models.CharField(max_length=255, blank=False)
    reward = models.CharField(max_length=255, blank=False)
    rewardTime = models.DateTimeField()
    signNumber = models.IntegerField(default=0, blank=False)
