from __future__ import absolute_import

from celery import shared_task
from .models import Configuration
from datetime import datetime 
import api.models, json, logging, pytz
from django.conf import settings  # noqa
from .helpers import require_lock
from django.db import transaction
from itertools import islice
import ast 
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_utils import to_bytes, to_hex, to_text

from .helpers import require_lock
from django.db import transaction

rpc = Web3(Web3.HTTPProvider(settings.RESTFUL_ENDPOINT))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

log = logging.getLogger('ming')

@shared_task
#@transaction.atomic
#@require_lock(api.models.epoch.Epoch,'ACCESS EXCLUSIVE')
def ProcessEpoch(block_num):
	blk = rpc.eth.getBlock(to_hex(block_num))
	#blk = api.models.block.Block.objects.get(id=block_id)
	slashedNode = []
	epoch = blk.number // settings.BLOCKS_PER_EPOCH
	log.info('\tProcessing epoch at block {0}.'.format(block_num))
	if epoch > 0:
		end_block = blk.number - 1
		start_block = end_block - settings.BLOCKS_PER_EPOCH + 1
		s_b = rpc.eth.getBlock(to_hex(start_block))
		e,created = api.models.epoch.Epoch.objects.get_or_create(
			epoch = epoch,
			defaults = {
				'epoch':epoch,
				'startTime': pytz.utc.localize(datetime.fromtimestamp(float(s_b.timestamp))),
				'endTime': pytz.utc.localize(datetime.fromtimestamp(float(blk.timestamp))),
				'startBlock': start_block,
				'endBlock': end_block,
				'isActive': False,
			},
		)
		e.startTime= pytz.utc.localize(datetime.fromtimestamp(float(s_b.timestamp)))
		e.isActive = False
		ne,necreated = api.models.epoch.Epoch.objects.get_or_create(
			epoch = epoch + 1,
			defaults = {
				'epoch':epoch + 1,
				'startTime':pytz.utc.localize(datetime.fromtimestamp(float(s_b.timestamp))),
				'endTime':pytz.utc.localize(datetime.fromtimestamp(float(s_b.timestamp))),
				'startBlock': blk.number,
				'endBlock': blk.number + settings.BLOCKS_PER_EPOCH - 1,
				'isActive': True,
			},
		)
		e.save()
		ne.save()
		if (blk.penalties != "0x"):
			for addr in zip(islice(blk.penalties[2:], 0, None, 20)):
				if addr.len() > 0:
					slashedNode.append(addr)

				if (slashedNode.len() > 0):
					for i in range(0,4):
						nextEpoch = epoch + 1 + i
						e,created = api.models.epoch.Epoch.objects.get_or_create(
							epoch = nextEpoch,
							defaults = {
								'epoch':nextEpoch,
								'startTime':pytz.utc.localize(datetime.fromtimestamp(float(s_b.timestamp))),
								'startBlock': ((nextEpoch - 1) * settings.BLOCKS_PER_EPOCH),
								'endBlock': (nextEpoch * settings.BLOCKS_PER_EPOCH) - 1,
								'isActive': False,
								'slashedNode': str(slashedNode)
							},
						)
						if not created:
							e.slashedNode = str(ast.literal_eval(e.slashedNode).extend(slashedNode))
						e.save()

@shared_task
def ProcessRewards(block_num):
	log.info('\tCalculating masternode rewards at block {0}.'.format(block_num))
	#blk = api.models.block.Block.objects.get(id=block_id)
	blk = rpc.eth.getBlock(to_hex(block_num))
	reward_req_data = {
			'jsonrpc': '2.0',
			'method': 'eth_getRewardByHash',
			'params': [ str(to_hex(blk.hash)) ],
			'id': settings.CHAIN_ID
	}
	result = requests.post(url=settings.RESTFUL_ENDPOINT, json=reward_req_data)
	data = result.json()['result']
	#log.warning(data)
	try:
		pass
	except requests.exceptions.RequestException as err:
		log.error('Exception calling RPC request {0}'.format(reward_req_data))
	except requests.exceptions.HTTPError as errh:
		log.error('HTTP Error calling RPC request {0}'.format(reward_req_data))
	except requests.exceptions.ConnectionError as errc:
		log.error('Connection Error calling RPC request {0}'.format(reward_req_data))
	except requests.exceptions.Timeout as errt:
		log.error('Timeout calling RPC request {0}'.format(reward_req_data))
