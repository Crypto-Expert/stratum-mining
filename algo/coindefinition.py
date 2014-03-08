import lib.logger
import lib.settings as settings
log = lib.logger.get_logger('Coin Definition')
log.debug("Got to Coin Definition")
from algo import *
from hashlib import sha256
import util

class BaseCoin(object):
    """
    Base class for coins. Defines the properties that need to be overridden.
    BaseCoin uses Bitcoin as the base algorithm. For Alt coins override any
    relevant functions.
    """

    @property
    def hash_bin(self, header_bin):
        """
        The hashing algorithm that is used for proof of work (Binary?)
	Location: lib/template_registry.py#L232 
        """
        return util.doublesha(''.join([ header_bin[i*4:i*4+4][::-1] for i in range(0, 20) ]))

    @property
    def calc_algo(self, nVersion, hashPrevBlock, hashMerkleRoot, nTime, nBits, nNonce):
	"""
	Builds Data Inside the BLOCKS
	Location: lib/halfnode.py#L250
	"""
        if self.algo is None:
           r = []
           r.append(struct.pack("<i", nVersion))
           r.append(ser_uint256(      hashPrevBlock))
           r.append(ser_uint256(      hashMerkleRoot))
           r.append(struct.pack("<I", nTime))
           r.append(struct.pack("<I", nBits))
           r.append(struct.pack("<I", nNonce))
	   self.algo = uint256_from_str(SHA256.new(SHA256.new(''.join(r)).digest()).digest())
        return self.algo

    @property
    def diff1(self):
        """
        The target for diff1
	Location: lib/template_registry.py#L145 
        """
        return 0x00000000ffff0000000000000000000000000000000000000000000000000000

    @property
    def header(self, header_hex):
	"""
	The Header_Hex Needs Padding?
	Location lib/template_registry.py#L262
	"""
	return header_hex = header_hex

    @property
    def block_hash_hex(self, header_bin):
	"""
	The Block Hewader
	Location lib/template_registry.py#L289
	"""
	block_hash_bin = util.doublesha(''.join([ header_bin[i*4:i*4+4][::-1] for i in range(0, 20) ]))
        block_hash_hex = block_hash_bin[::-1].encode('hex_codec')
	return block_hash_hex



    
