from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings  # noqa

STATUS = (
   ('PROPOSED', _('Proposed to be a masternode')),
   ('RESIGNED', _('Resigned from masternodes')),
   ('SLASHED', _('Slashed from masternodes')),
   ('MASTERNODE', _('Currently a masternode')),
)

class Candidate (models.Model):
	smartContractAddress = models.CharField(max_length=255,db_index=True,blank=False)
	owner = models.CharField(max_length=255,db_index=True,blank=False)
	candidate = models.CharField(max_length=255,db_index=True,blank=False)
	nodeId = models.IntegerField(default=0)
	name = models.CharField(max_length=255,blank=True)
	capacity = models.CharField(max_length=255,blank=True)
	capacityNumber = models.DecimalField(default=0,max_digits=99,decimal_places=18)
	latestBlock = models.CharField(max_length=255,blank=True)
	totalSignedBlocks = models.CharField(max_length=255,blank=True)
	rewarded = models.CharField(max_length=255,blank=True)
	hardware  = models.CharField(max_length=255,blank=True)
	dc_name = models.CharField(max_length=255,blank=True)
	dc_location = models.CharField(max_length=255,blank=True)
	lastSignedBlock = models.IntegerField(default=0)
	github = models.CharField(max_length=255,blank=True)
	linkedin = models.CharField(max_length=255,blank=True)
	email  = models.CharField(max_length=255,blank=True)
	website = models.CharField(max_length=255,blank=True)
	telegram = models.CharField(max_length=255,blank=True)
	status  = models.CharField(max_length=255,blank=True,db_index=True,choices=STATUS)
	rank = models.IntegerField(default=0)

	@property
	def isMasternode(self):
		return (self.status == 'MASTERNODE' or self.status == 'SLASHED')

def active_candidates(sort_by='capacity'):
	total = Candidate.objects.filter(smartContractAddress=settings.VALIDATOR_CONTRACT_ADDRESS).order_by(sort_by)[:200]
	active = Candidate.objects.filter(smartContractAddress=settings.VALIDATOR_CONTRACT_ADDRESS).exclude(status='RESIGNED').order_by(sort_by)[:200]
	return { 'total': total, 'active': active }

class Voter (models.Model):
    smartContractAddress = models.CharField(max_length=255,db_index=True,blank=False)
    voter = models.CharField(max_length=255,db_index=True,blank=False)
    candidate = models.CharField(max_length=255,db_index=True,blank=False)
    capacity = models.CharField(max_length=255,db_index=True,blank=False)
    capacityNumber = models.DecimalField(default=0,max_digits=99,decimal_places=18)

class Withdraw (models.Model):
    smartContractAddress = models.CharField(max_length=255,db_index=True,blank=False)
    tx = models.CharField(max_length=255,db_index=True,blank=False)
    owner = models.CharField(max_length=255,db_index=True,blank=False)
    blockNumber = models.CharField(max_length=255,db_index=True,blank=False)
    capacity = models.CharField(max_length=255,blank=False)
