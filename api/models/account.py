from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Account(models.Model):
	_hash = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
	balance = models.CharField(max_length=255, blank=True)
	balance_number = models.DecimalField(default=0,max_digits=99,decimal_places=18)
	code = models.TextField(blank=True)
	inTxCount = models.IntegerField(_('inTxCount'), default=0)
	outTxCount = models.IntegerField(_('outTxCount'), default=0)
	totalTxCount =  models.IntegerField(_('totalTxCount'), default=0)
	internalTxCount =  models.IntegerField(_('internalTxCount'), default=0)
	tokenTxCount =  models.IntegerField(_('tokenTxCount'), default=0)
	minedBlock =  models.IntegerField(_('minedBlock'), default=0)
	rewardCount =  models.IntegerField(_('rewardCount'), default=0)
	logCount =  models.IntegerField(_('logCount'), default=0)
	contractCreation = models.CharField(max_length=4096, blank=True)
	isContract = models.BooleanField(default=True)
	storageAt = models.CharField(max_length=4096, blank=True)
	status = models.BooleanField(default=False)
	@property
	def hash(self):
		return self._hash
	

class SpecialAccount (models.Model):
	_hash = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
	total = models.IntegerField(_('total'), default=0)
	pending = models.IntegerField(_('pending'), default=0)
	sign = models.IntegerField(_('sign'), default=0)
	other = models.IntegerField(_('other'), default=0)

class Signature (models.Model):
	signedAddress = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
	signedAddressId = models.CharField(max_length=255, blank=False, db_index=True)
	message = models.TextField(blank=True)
	signature = models.TextField(blank=True)
