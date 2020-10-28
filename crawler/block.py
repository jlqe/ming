from __future__ import absolute_import

from django.db.models import F
from celery import shared_task
from .models import Configuration
from .tx import ProcessTransaction
from .epoch import ProcessEpoch, ProcessRewards
from .masternode import ProcessMasternodes
from datetime import datetime 
import api.models, json, logging, pytz
from django.conf import settings  # noqa
from django.db import transaction
from itertools import islice
import ast 
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_utils import to_bytes, to_hex, to_text
rpc = Web3(Web3.HTTPProvider(settings.RESTFUL_ENDPOINT))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

log = logging.getLogger('ming')

@shared_task
def ProcessBlock(block_num):
	epoch = block_num // settings.BLOCKS_PER_EPOCH
	log = logging.getLogger('ming')
	log.warning('Processing epoch #{1}, block #{0}'.format(block_num, epoch))
	block_data = rpc.eth.getBlock(block_num)
	log.debug('\tBlock data received')

	_block = api.models.block.Block.objects.get_or_create(_hash = to_hex(block_data.hash), defaults = { 'timestamp':pytz.utc.localize(datetime.fromtimestamp(float(block_data.timestamp)))})[0]
	_block.number = block_data.number
	_block._hash = to_hex(block_data.hash)
	_block.parentHash = to_hex(block_data.parentHash)
	_block.nonce = to_hex(block_data.nonce)
	_block.sha3Uncles = to_hex(block_data.sha3Uncles)
	_block.logsBloom = to_hex(block_data.logsBloom)
	_block.transactionsRoot = to_hex(block_data.transactionsRoot)
	_block.stateRoot = to_hex(block_data.stateRoot)
	_block.receiptsRoot = to_hex(block_data.receiptsRoot)
	_block.miner = block_data.miner
	_block.difficulty = block_data.difficulty
	_block.totalDifficulty = block_data.totalDifficulty
	_block.extraData = to_bytes(block_data.proofOfAuthorityData)
	_block.size = block_data.size
	_block.gasLimit = block_data.gasLimit
	_block.gasUsed = block_data.gasUsed
	_block.timestamp = pytz.utc.localize(datetime.fromtimestamp(float(block_data.timestamp)))
	_block.mixHash = to_hex(block_data.mixHash)
	_block.validator = block_data.validator
	_block.validators = block_data.validators
	_block.transactions = block_data.transactions
	_block.uncles = block_data.uncles
	_block.e_tx = len(block_data.transactions)
	_block.status=True
	_block.signer,_block.m2 = _block.getM1M2()
	_block.save()
	# update block finality
	#r = api.models.block.Block.objects.filter(number__lt=block_num, finality__lt=100).update(finality=F('finality')+1)

	log.debug('\tBlock saved.')

@shared_task
def ProcessBlockSigners(block_num):
	blk = rpc.eth.getBlock(to_hex(block_num))
	#blk = api.models.block.Block.objects.get(id=block_id)
	signer_req_data = {
			'jsonrpc': '2.0',
			'method': 'eth_getBlockSignersByHash',
			'params': [ str(to_hex(blk.hash)) ],
			'id': settings.CHAIN_ID,
	}
	result = requests.post(url=settings.RESTFUL_ENDPOINT, json=signer_req_data)
	data = result.json()['result']
	api.models.block.BlockSigner.objects.update()
	blocksigner=api.models.block.BlockSigner.objects.get_or_create(blockNumber=blk.number,defaults={ 'blockNumber':blk.number, 'blockHash':blk.hash, 'signers':data})[0]
	blocksigner.save()
	try:
		pass
	except:
		log.error('Error calling RPC request {0}'.format(signer_req_data))

