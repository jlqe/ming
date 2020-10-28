from __future__ import absolute_import

from celery import shared_task

from .models import Configuration
from .block import ProcessBlock, ProcessBlockSigners
from .epoch import ProcessEpoch, ProcessRewards
from .masternode import ProcessMasternodes
from .tx import ProcessTransaction

from datetime import datetime 
import api.models, json, logging, pytz
from django.conf import settings  # noqa
from itertools import islice
import ast , time
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_utils import to_bytes, to_hex
rpc = Web3(Web3.HTTPProvider(settings.RESTFUL_ENDPOINT))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

log = logging.getLogger('ming')

@shared_task
def Start():
	config, created = Configuration.objects.get_or_create(id=0,defaults={'lastblock': 0},)
	log.warning('Crawler started')
	while True:
		current = rpc.eth.getBlock('latest')
		if config.lastblock < current.number:
			ProcessBlock.delay(config.lastblock)
			ProcessTransaction.delay(config.lastblock)
			ProcessBlockSigners.delay(config.lastblock)
			if (config.lastblock % settings.BLOCKS_PER_EPOCH == 0):
				ProcessEpoch.delay(config.lastblock)
			# calculate rewards
			if (config.lastblock % 25 == 0):
				ProcessRewards.delay(config.lastblock)

			config.lastblock = config.lastblock + 1
			config.save()
			if (config.lastblock % 60 == 0):
				ProcessMasternodes.delay(config.lastblock)
			if config.lastblock < 3:
				time.sleep(5)

