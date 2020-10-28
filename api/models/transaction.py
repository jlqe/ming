from django.db import models
from django.utils.translation import gettext_lazy as _

from .block import Block

class TxAccount(models.Model):
    accountName = models.CharField(max_length=255)
    isContract = models.BooleanField(default=False)
    contractCreation = models.TextField(blank=True)

class Tx (models.Model):
    _hash = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
    nonce = models.IntegerField(default=0)
    blockHash = models.CharField(max_length=255, blank=False, db_index=True)
    blockNumber = models.IntegerField(default=0, db_index=True)
    transactionIndex = models.IntegerField(default=0)
    _from = models.CharField(max_length=255, blank=False, db_index=True)
    to = models.CharField(max_length=255, blank=False, db_index=True)
    value = models.CharField(max_length=255, blank=False)
    r = models.CharField(max_length=255, blank=False)
    s = models.CharField(max_length=255, blank=False)
    v = models.CharField(max_length=255, blank=False)
    gas = models.IntegerField(default=0)
    gasPrice = models.CharField(max_length=255, blank=False)
    _input = models.CharField(max_length=255, blank=False)
    contractAddress = models.CharField(max_length=255, blank=False, db_index=True)
    cumulativeGasUsed = models.IntegerField(default=0)
    gasUsed = models.IntegerField(default=0)
    from_model = models.OneToOneField(TxAccount, on_delete=models.CASCADE, blank=True, null=True)
    to_model = models.OneToOneField(TxAccount, on_delete=models.CASCADE, related_name = 'to', blank=True, null=True)
    status = models.BooleanField(default=False)
    isPending = models.BooleanField(default=False, db_index=True)
    e_tx = models.IntegerField(default=0)

    @property
    def hash(self):
        return self._hash
    

class TxReceipt (models.Model):
    blockHash = models.CharField(max_length=255, blank=False, db_index=True)
    blockNumber = models.BigIntegerField(default=0,db_index=True)
    contractAddress = models.CharField(max_length=255, blank=False)
    cumulativeGasUsed = models.IntegerField(default=0)
    logs = models.TextField()
    logsBloom = models.TextField(blank=False)
    root = models.CharField(max_length=255, blank=False)
    transactionHash = models.CharField(max_length=255, blank=False)
    transactionIndex = models.IntegerField(default=0)

class TxExtraInfo (models.Model):
    transactionHash = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
    infoName = models.CharField(max_length=255, blank=False)
    infoValue = models.CharField(max_length=255, blank=False)

class InternalTx (models.Model):
    _hash = models.CharField(db_index=True, max_length=255)
    _from = models.CharField(db_index=True, max_length=255)
    to = models.CharField(db_index=True, max_length=255)
    blockNumber = models.IntegerField(db_index=True, default=0)
    blockHash = models.CharField(db_index=True, max_length=255)
    value = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
