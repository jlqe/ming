from __future__ import absolute_import

from celery import shared_task
from .models import Configuration
from .helpers import require_lock
from datetime import datetime 
import api.models, json, logging, pytz
from django.conf import settings  # noqa
from django.db import transaction
from django.db.models import Count
from itertools import islice
import ast 
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import ContractEvent

from eth_utils import to_bytes, to_hex, from_wei

rpc = Web3(Web3.HTTPProvider(settings.RESTFUL_ENDPOINT))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

log = logging.getLogger('ming')


f = open('{0}/contracts/TaoValidator.abi'.format(settings.BASE_DIR), 'r')
ValidatorABI = json.load(f)
validator = rpc.eth.contract(abi=ValidatorABI, address=settings.VALIDATOR_CONTRACT_ADDRESS)

@shared_task
#@transaction.atomic
#@require_lock(api.models.shifu.Candidate,'ACCESS EXCLUSIVE')
def ProcessMasternodes(block_num):
	log.info('\tProcessing masternode validation at block {0}.'.format(block_num))
	#blk = api.models.block.Block.objects.get(id=block_id)
	blk = rpc.eth.getBlock(to_hex(block_num))
	signer_req_data = {
			'jsonrpc': '2.0',
			'method': 'eth_getCandidates',
			'params': [ 'latest' ],
			'id': settings.CHAIN_ID,
	}
	result = requests.post(url=settings.RESTFUL_ENDPOINT, json=signer_req_data)
	data = result.json()['result']

	for c in data['candidates']:
		d = data['candidates'][c]
		owner = validator.functions.getCandidateOwner(c).call()
		cand = api.models.shifu.Candidate.objects.filter(smartContractAddress=settings.VALIDATOR_CONTRACT_ADDRESS, candidate=c)
		if len(cand) < 1:
			cand = api.models.shifu.Candidate()
		else:
			cand = cand[0]
		cand.smartContractAddress = settings.VALIDATOR_CONTRACT_ADDRESS
		cand.owner = owner
		cand.candidate = c
		cand.status = d['status']
		cand.capacity  = d['capacity']
		cand.capacityNumber = from_wei(d['capacity'],'ether')
		if d['status'] == 'MASTERNODE' or d['status'] == 'SLASHED':
			cand.latestBlock = blk.number
			cand.totalSignedBlocks = api.models.block.BlockSigner.objects.filter(signers__icontains=c).count()
			lsb = api.models.block.BlockSigner.objects.filter(signers__icontains=c).order_by('-blockNumber')
			if len(lsb) > 0:
				cand.lastSignedBlock = lsb[0].blockNumber
		cand.save()
		ProcessVoters(c,block_num)

	# update top 150 rankings
	top150 = api.models.shifu.Candidate.objects.values('id').annotate(capacity_cap=Count('capacityNumber')).order_by('-capacity_cap')[:150]
	rank = 1
	for x in top150:
		_c = api.models.shifu.Candidate.objects.get(id=x['id'])
		_c.rank = rank
		_c.save()
		rank += 1

#@transaction.atomic
#@require_lock(api.models.shifu.Voter,'ACCESS EXCLUSIVE')
def ProcessVoters(c,block_num):
	log.info('\t\tProcessing masternode voters at block {0}.'.format(block_num))
	voters = validator.functions.getVoters(c).call()
	for v in voters:
		voter_cap = validator.functions.getVoterCap(c,v).call()
		voter = api.models.shifu.Voter.objects.get_or_create(smartContractAddress=settings.VALIDATOR_CONTRACT_ADDRESS, voter=v,candidate=c, defaults=
			{
				'smartContractAddress': settings.VALIDATOR_CONTRACT_ADDRESS,
				'voter': v,
				'candidate': c,
				'capacity': voter_cap,
				'capacityNumber' : from_wei(voter_cap,'ether')
			})[0]
		voter.save()
