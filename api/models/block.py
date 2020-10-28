from django.db import models
from django.utils.translation import gettext_lazy as _

import eth_keys 
from eth_utils import to_hex, add_0x_prefix
from eth.abc import BlockHeaderAPI as BlockHeader 
from eth_typing import HexStr
import web3
from web3 import Web3
from web3.auto import w3


class Block(models.Model):
    number = models.BigIntegerField(default=0)
    _hash = models.CharField(max_length=255, blank=False, db_index=True, unique=True)
    parentHash = models.CharField(max_length=255, blank=False, db_index=True)
    nonce = models.CharField(max_length=255, blank=False, db_index=True)
    sha3Uncles = models.TextField(blank=True)
    logsBloom = models.TextField(blank=True)
    transactionsRoot = models.CharField(max_length=255, blank=False)
    stateRoot = models.CharField(max_length=255, blank=False)
    receiptsRoot = models.CharField(max_length=255, blank=False)
    miner = models.CharField(max_length=255, blank=False)
    difficulty = models.CharField(max_length=255, blank=False)
    totalDifficulty = models.CharField(max_length=255, blank=False)
    extraData = models.TextField( blank=True)
    size = models.IntegerField(default=0)
    gasLimit = models.IntegerField(default=0)
    gasUsed = models.IntegerField(default=0)
    timestamp = models.DateTimeField(blank=False)
    uncles = models.TextField(blank=True)
    mixHash = models.TextField(blank=False, db_index=True)
    penalties = models.TextField()
    signer = models.CharField(max_length=255, blank=False, db_index=True)
    m2 = models.CharField(max_length=255, blank=False, db_index=True)
    status = models.BooleanField(default=False)
    finality = models.IntegerField(default=0,db_index=True)
    updateFinalityTime = models.IntegerField(default=0, db_index=True)
    e_tx = models.IntegerField(default=0)
    validator = models.CharField(max_length=255, blank=False, db_index=True)
    validators = models.TextField(blank=False, db_index=True)
    transactions = models.TextField(blank=True)

    class Meta:
        ordering = ['number']
        
    @property
    def hash(self):
        return self._hash
    
    def getM1M2(self):
        m1 = add_0x_prefix(to_hex(self.extraData)[66:106])

        m2 = self.validator
        return m1,m2

class BlockSigner(models.Model):
    blockNumber = models.BigIntegerField(default=0, db_index=True)
    blockHash = models.CharField(max_length=255, blank=False, db_index=True)
    signers = models.TextField()

