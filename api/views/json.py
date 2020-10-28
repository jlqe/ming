from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse

APPROVED_RPC = [
	'eth_accounts',
	'eth_blockNumber',
	'eth_call',
	'eth_chainId',
	'eth_estimateGas',
	'eth_gasPrice',
	'eth_getBalance',
	'eth_getBlockByHash',
	'eth_getBlockByNumber',
	'eth_getBlockTransactionCountByHash',
	'eth_getBlockTransactionCountByNumber',
	'eth_getCode',
	'eth_getLogs',
	'eth_getStorageAt',
	'eth_getTransactionByBlockHashAndIndex',
	'eth_getTransactionByBlockNumberAndIndex',
	'eth_getTransactionByHash',
	'eth_getTransactionCount',
	'eth_getTransactionReceipt',
	'eth_getUncleByBlockHashAndIndex',
	'eth_getUncleByBlockNumberAndIndex',
	'eth_getUncleCountByBlockHash',
	'eth_getUncleCountByBlockNumber',
	'eth_protocolVersion',
	'eth_sendRawTransaction',
	'eth_syncing',
	'net_listening',
	'net_peerCount',
	'net_version',
	'web3_clientVersion',
]

@api_view(['GET'])
def JsonRpc(request):
	# filter only approved RPC calls
	try:
		data = request.data	
	except:
		return JsonResponse(status=400)

	method = data['method']
	if method in APPROVED_RPC:
		params = data['params']
		chain_id = data['id']
		geth_req = {
				'jsonrpc': '2.0',
				'method': method,
				'params': params,
				'id': chain_id,
		}
		try:
			result = requests.post(url=settings.RESTFUL_ENDPOINT, json=geth_req)
			return result.json()['result']
		except:
			return JsonResponse(status=500)
	else:
		return JsonResponse(status=500)
