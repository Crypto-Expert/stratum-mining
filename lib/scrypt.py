import basecoin
import lib.logger
import struct

''' This import was intended for the import_algo method, but I have not had luck
    with it being picked up there'''
import ltc_scrypt

from util import *
from Crypto.Hash import SHA256
logger = lib.logger.get_logger('Coin Definition')
logger.debug("Got to Coin Definition")
Base = basecoin.Base

class Coin(Base):
   def __init__(self):
       self.algo = 'scrypt'
       self.import_algo

   @classmethod
   def import_algo(self):
       
       return self.algo
       
   @classmethod
   def hash_bin(self, header_bin):
       """
       The Hashing Algorithm Used
       """
       hash_bin = ltc_scrypt.getPoWHash(''.join([ header_bin[i*4:i*4+4][::-1] for i in range(0, 20) ]))
       return hash_bin

   @classmethod
   def block_hash_bin(self, header_bin):
       """
       The Block Hashing Algorithm Used
       """
       hash_bin = doublesha(''.join([ header_bin[i*4:i*4+4][::-1] for i in range(0, 20) ]))
       return hash_bin

   @classmethod
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
       return r;

   @classmethod
   def return_diff1(self):
       """
       Returns the difficulty of a diff1 share which is used to calc share diff
       """
       return 0x0000ffff00000000000000000000000000000000000000000000000000000000

   @classmethod
   def padding(self, header_hex):
       """
       Does the Header Need Padding?
       """
       return header_hex + "000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000"

   @classmethod
   def build_header(self, block_hash_bin):
       """
       Returns data needed to build the block header
       """
       return block_hash_bin[::-1].encode('hex_codec')

   @classmethod
   def calc_algo(r):
       """
       builds block
       """
       return uint256_from_str(ltc_scrypt.getPoWHash(''.join(r)))
