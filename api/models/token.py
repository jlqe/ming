from django.db import models
from django.utils.translation import gettext_lazy as _

TOKEN_TYPES = (
    'TRC20',
    'TRC21',
    'TRC721',
    'OTHER'
    )

TOKEN_FUNCTIONS = {
                    'decimals': '0x313ce567', # hex to decimal
                    'symbol': '0x95d89b41', # hex to ascii
                    'totalSupply': '0x18160ddd',
                    'transfer': '0xa9059cbb',
                    'name': '0x06fdde03',
                }
TRC20_FUNCTIONS = {
    'totalSupply': '0x18160ddd',
    'balanceOf': '0x70a08231',
    'allowance': '0xdd62ed3e',
    'transfer': '0xa9059cbb',
    'approve': '0x095ea7b3',
    'transferFrom': '0x23b872dd',
    'Transfer': '0xddf252ad',
    'Approval': '0x8c5be1e5',
    'name': '0x06fdde03',
    'symbol': '0x95d89b41',
    'decimals': '0x313ce567'
}
TRC21_FUNCTIONS = {
    'totalSupply': '0x18160ddd',
    'balanceOf': '0x70a08231',
    'estimateFee': '0x127e8e4d',
    'issuer': '0x1d143848',
    'allowance': '0xdd62ed3e',
    'transfer': '0xa9059cbb',
    'approve': '0x095ea7b3',
    'transferFrom': '0x23b872dd',
    'Transfer': '0xddf252ad',
    'Approval': '0x8c5be1e5',
    'Fee': '0xfcf5b327',
    'name': '0x06fdde03',
    'symbol': '0x95d89b41',
    'decimals': '0x313ce567',
    'minFee': '0x24ec7590'
}
TRC721_FUNCTIONS = {
    'Transfer': '0xddf252ad',
    'Approval': '0x8c5be1e5',
    'ApprovalForAll': '0x17307eab',
    'balanceOf': '0x70a08231',
    'ownerOf': '0x6352211e',
    'safeTransferFrom1': '0xb88d4fde',
    'safeTransferFrom': '0x42842e0e',
    'transferFrom': '0x23b872dd',
    'approve': '0x095ea7b3',
    # 'setApprovalForAll': '0xa22cb465',
    'getApproved': '0x081812fc',
    # 'isApprovedForAll': '0x7070ce33',
    'supportsInterface': '0x01ffc9a7',
    'totalSupply': '0x18160ddd'
}

TOPIC_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

class TokenTx (models.Model):
    address = models.CharField(max_length=255,db_index=True)
    blockHash = models.CharField(max_length=255,db_index=True)
    blockNumber = models.BigIntegerField(default=0,db_index=True)
    transactionHash = models.CharField(max_length=255,db_index=True)
    transactionIndex = models.IntegerField(default=0)
    tokenId = models.IntegerField(default=0, blank=True)
    _from = models.CharField(max_length=255,db_index=True)
    to = models.CharField(max_length=255,db_index=True)
    data = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    valueNumber = models.DecimalField(default=0,max_digits=99,decimal_places=18)
    _input = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    _type = models.CharField(max_length=255,db_index=True)


class Token (models.Model):
    _hash = models.CharField(max_length=255, unique=True, db_index=True)
    website = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    icoInfo = models.TextField(blank=True)
    status = models.BooleanField(default=False)
    _type = models.CharField(max_length=255)
    decimals = models.IntegerField(default=0,blank=True)
    totalSupply = models.CharField(max_length=255)
    totalSupplyNumber = models.DecimalField(default=0,max_digits=99,decimal_places=18)

    @property
    def isMintable(self,code):
        mintFunction = '0x40c10f19'
        if mintFunction in code:
            return True
        else:
            return False

    def getFunction(self,name):
        if self._type == 'TRC20':
            funcs = TRC20_FUNCTIONS
        elif self._type == 'TRC21':
            funcs = TRC21_FUNCTIONS
        elif self._type == 'TRC721':
            funcs = TRC721_FUNCTIONS
        return funcs[name]