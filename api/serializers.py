from rest_framework import serializers
from api.models import *

class BlockSerializer(serializers.ModelSerializer):
	class Meta:
		model = block.Block
		fields = '__all__' 

class BlockSignerSerializer(serializers.ModelSerializer):
	class Meta:
		model = block.BlockSigner
		fields = '__all__' 
