from __future__ import absolute_import

from .helpers import invalid_xml_remove
from celery import shared_task
from .models import Configuration
from datetime import datetime 
import api.models, json, logging, pytz
from django.conf import settings  # noqa
from itertools import islice
import ast 
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_utils import to_bytes, to_hex, from_wei, to_int
rpc = Web3(Web3.HTTPProvider(settings.RESTFUL_ENDPOINT))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

log = logging.getLogger('ming')
DEFAULT_ABI = [
	{
		'constant': True,
		'inputs': [
			{
				'name': 'tokenOwner',
				'type': 'address'
			}
		],
		'name': 'balanceOf',
		'outputs': [
			{
				'name': 'balance',
				'type': 'uint256'
			}
		],
		'payable': False,
		'stateMutability': 'view',
		'type': 'function'
	},
	{
		'constant': True,
		'inputs': [
			{
				'name': 'tokenOwner',
				'type': 'address'
			},
			{
				'name': 'spender',
				'type': 'address'
			}
		],
		'name': 'allowance',
		'outputs': [
			{
				'name': 'remaining',
				'type': 'uint256'
			}
		],
		'payable': False,
		'stateMutability': 'view',
		'type': 'function'
	}
]


@shared_task
def ProcessTransaction(block_num):
	block_data = rpc.eth.getBlock(block_num)
	for tx_hash in block_data['transactions']:
		log.info('\t\t Transaction {0}.'.format(to_hex(tx_hash)))
		tx = rpc.eth.getTransaction(tx_hash)
		txreceipt = rpc.eth.getTransactionReceipt(tx_hash)
		api.models.transaction.Tx.objects.update()
		_tx, created = api.models.transaction.Tx.objects.get_or_create(_hash=tx_hash)
		_tx._hash = to_hex(tx_hash)
		_tx.nonce = tx.nonce
		_tx.blockHash = to_hex(tx.blockHash)
		_tx.blockNumber = tx.blockNumber
		_tx.transactionIndex = tx.transactionIndex
		_tx._from = tx['from']
		_tx.to = tx.to
		_tx.value = tx.value
		_tx.gas = tx.gas
		_tx.gasPrice = tx.gasPrice
		_tx._input = tx.input
		_tx.r = to_hex(tx.r)
		_tx.s = to_hex(tx.s) 
		_tx.v = to_hex(tx.v)
		_tx.cumulativeGasUsed = txreceipt.cumulativeGasUsed
		_tx.gasUsed = txreceipt.gasUsed
		#_tx.status = (to_int(txreceipt.status) == 1)
		_tx.isPending = False
		_tx.save()

		ParseTxLog.delay(to_hex(tx_hash),block_num)

		fromIsTaoContract = (_tx._from is settings.SIGNER_CONTRACT_ADDRESS or _tx._from is settings.RANDOMIZER_CONTRACT_ADDRESS) 
		toIsTaoContract = (_tx.to is settings.SIGNER_CONTRACT_ADDRESS or _tx.to is settings.RANDOMIZER_CONTRACT_ADDRESS) 
		if _tx._from is not None:
			if not fromIsTaoContract:
				from_account = api.models.account.Account.objects.get_or_create(_hash=_tx._from, defaults={'_hash':_tx._from})[0]
				from_account.save()
		if _tx.to is not None:
			if not toIsTaoContract:
				to_account = api.models.account.Account.objects.get_or_create(_hash=_tx.to, defaults={'_hash':_tx.to})[0]
				to_account.save()
		else:
			if (txreceipt.contractAddress is not None):
				contractAddress = to_hex(txreceipt.contractAddress)				
				to_account = api.models.account.Account.objects.get_or_create(_hash=_tx.to, defaults={'_hash':_tx.to})[0]
				_tx.contractAddress = contractAddress
				_tx.to = contractAddress
				_tx.contractCreation = to_hex(tx._from) 
				to_account.isContract = True
				to_account.save()
				_tx.save()
				try:
					internal_req_data = {
							'jsonrpc': '2.0',
							'method': 'debug_traceTransaction',
							'params': [_tx._hash, { 'tracer': 'callTracer', 'timeout': '10s' }],
							'id': settings.CHAIN_ID,
					}
					result = requests.post(url=settings.RESTFUL_ENDPOINT, json=internal_req_data)
				except:
					log.error('ERROR: Cannot contact RPC attempting to debug transaction.')
				finally:
					data = result.json()['result']
					calls = data['calls']
					ProcessInternalTx.delay(calls)							

		f = ProcessAccount(_tx.id,from_account.id)
		t = ProcessAccount(_tx.id,to_account.id)

		txamt = from_wei(_tx.value,'ether')
		if txamt > 20000:
			#TODO post to twitter
			pass 

def ProcessAccount(tx_id,acct_id):
	acct = api.models.account.Account.objects.get(id=acct_id)
	log.info('\t\t Account {0}.'.format(acct.hash))
	_tx = api.models.transaction.Tx.objects.get(id=tx_id)
	balance = rpc.eth.getBalance(acct.hash)
	code = to_hex(rpc.eth.getCode(acct.hash))
	if code != '0x':
		acct.isContract = True
		acct.isToken = checkIsToken(code)
		if acct.isToken:
			token = api.models.token.TokenInfo.objects.get_or_create(_hash=acct.hash,default={'_hash':acct.hash})
			token._type = getTokenType()
			token.save()

	acct.code = code
	acct.status = True
	acct.balance = balance
	acct.balance_number = from_wei(balance,'ether')
	acct.save()
	return acct

@shared_task
def ParseTxLog(tx_hash,block_num):
	block_data = rpc.eth.getBlock(block_num)
	txr = rpc.eth.getTransactionReceipt(tx_hash)
	logs = txr.logs
	if len(logs) < 1:
		return 
	l = logs[0]
	if len(l.topics) < 3:
		return
	if l.topics[0] == api.models.token.TOPIC_TRANSFER:
		ttype = getTokenType(l)
		fungible = (ttype == 'TRC20' or ttype == 'TRC21')
		token, created = api.models.token.Token.objects.get_or_create(_hash=to_hex(l.address),default={'_hash':to_hex(l.address), '_type': ttype})
		if created:
			token.name = invalid_xml_remove(to_string(rpc.eth.call({ 'to': token._hash, 'data': token.getFucntion('name') })))
			token.totalSupply = to_string(rpc.eth.call({ to: address, data: api.models.token.TOKEN_FUNCTIONS['totalSupply'] }))
			token.totalSupplyNumber = from_wei(to_int(rpc.eth.call({ to: address, data: api.models.token.TOKEN_FUNCTIONS['totalSupply'] })))
			if fungible:
				token.decimals = to_int(rpc.eth.call({ to: address, data: api.models.token.TOKEN_FUNCTIONS['decimals'] }))
				token.symbol = invalid_xml_remove(to_string(rpc.eth.call({ 'to': token._hash, 'data': token.getFucntion('symbol') })))
				token.save()
		address = token._hash
		if (l.topics[1]):
			txfrom = to_hex(l.topics[1])
		if (l.topics[2]):
			txto = to_hex(l.topics[2])
		if fungible:
			decimals = token.decimals
			value = to_int(l.data)
			valueNumber = float(value / 10 ** decimals)
		else:
			value = 0
			valueNumber = 0 
		token_tx = api.models.token.TokenTx.objects.get_or_create(address=address,
		transactionHash=to_hex(txr.transactionHash), default={
			'_hash': address,
			'blockHash': to_hex(txr.blockHash),
			'blockNumber': txr.blockNumber,
			'transactionHash': to_hex(txr.transactionHash),
			'transactionIndex': to_int(txr.transactionIndex),
			'_from': txfrom,
			'to': txto,
			'data': txr.data,
			'value': value,
			'valueNumber': valueNumber,
			'_input': txr['input'],
			'timestamp': pytz.utc.localize(datetime.fromtimestamp(float(block_data.timestamp))),
			'tokenId' : None,
			'_type' : ttype
		})
		if token._type == 'TRC721':
			token_tx.tokenId = to_int(l.topics[3])
		token_tx.save()

def getTokenType(l):
	if l.code == "0x":
		return
	if l.code in TRC20_FUNCTIONS:
		ttype = 'TRC20'
	if l.code in TRC21_FUNCTIONS:
		ttype = 'TRC21'
	if l.code in TRC721_FUNCTIONS:
		ttype = 'TRC721'
	return ttype

def checkIsToken(code):
	for func in api.models.token.TOKEN_FUNCTIONS:
		if func[1][2:] == code:
			return True
	return False

@shared_task
def ProcessInternalTx(calls):
	for call in calls:
		if call.value != '0x0':
			internalTx = api.models.transaction.InternalTx.objects.get_or_create(_hash = _tx._hash, default=
				{
					'_hash':_tx._hash,
					'blockNumber':block_num,
					'blockHash':to_hex(block_data.hash),
					'to':call.to,
					'_from':call['from'],
					'value':to_text(call.value),
					'timestamp': pytz.utc.localize(datetime.fromtimestamp(float(block_data.timestamp))),
				})
			if call.calls:
				ProcessInternalTx.delay(call.calls)