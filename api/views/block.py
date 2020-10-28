from api.models.block import Block, BlockSigner
from api.serializers import BlockSerializer, BlockSignerSerializer
from rest_framework import generics

class BlockList(generics.ListAPIView):
	"""
	Returns a list of blocks

	[ref]: http://ming.tao.network/blocks
	"""
	queryset = Block.objects.all()
	serializer_class = BlockSerializer

class BlockDetail(generics.RetrieveAPIView):
	"""
	Returns a blocks by block number

	[ref]: http://ming.tao.network/blocks/<block_number>
	"""
	queryset = Block.objects.all()
	serializer_class = BlockSerializer

class BlockSignerDetail(generics.RetrieveAPIView):
	"""
	Returns a list of block signers for a block

	[ref]: http://ming.tao.network/blocksigner/<block_number>
	"""
	queryset = BlockSigner.objects.all()
	serializer_class = BlockSignerSerializer

