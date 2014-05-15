import basecoin
import lib.logger
import struct
from util import *
from Crypto.Hash import SHA256
logger = lib.logger.get_logger('Coin Definition')
logger.debug("Got to Coin Definition")

class Base(object):
   """
   Base Class For Coins to Inherit Algorithm(SHA256)
   """
   def __init__(self):
       self.algo = None

   @property
   def import_algo(self):
       """
       Does an Algo Module need to be imported?
       """
       return self.algo
       
   @property
   def hash_bin(self, header_bin):
       """
       The Hashing Algorithm Used
       """
       hash_bin = doublesha(''.join([ header_bin[i*4:i*4+4][::-1] for i in range(0, 20) ]))
       return hash_bin

   @property
   def block_hash_bin(self, header_bin):
       """
       The Block Hashing Algorithm Used
       """
       hash_bin = self.hash_bin(header_bin)
       return hash_bin

   @property
   def build_block(self, nVersion, hashPrevBlock, hashMerkleRoot, nTime, nBits, nNonce):
       """
       Buids the Data For the Block
       """
       r = []
       r.append(struct.pack("<i", nVersion))
       r.append(ser_uint256(hashPrevBlock))
       r.append(ser_uint256(hashMerkleRoot))
       r.append(struct.pack("<I", nTime))
       r.append(struct.pack("<I", nBits))
       r.append(struct.pack("<I", nNonce))
       return r

   @property
   def return_diff1(self):
       """
       Returns the difficulty of a diff1 share which is used to calc share diff
       """
       return 0x00000000ffff0000000000000000000000000000000000000000000000000000

   @property
   def padding(self, header_hex):
       """
       Does the Header Need Padding?
       """
       return header_hex # Return Header + Padding if needed

   @property
   def build_header(self, block_hash_bin):
       """
       Returns data needed to build the block header
       """
       return block_hash(block_hash_bin)[::-1].encode('hex_codec')

   @property
   def calc_algo(r):
       """
       builds block
       """
       return  uint256_from_str(SHA256.new(SHA256.new(''.join(r)).digest()).digest())
