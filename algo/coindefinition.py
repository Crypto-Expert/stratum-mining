import lib.logger
import struct
from lib.util import ser_uint256, doublesha


logger = lib.logger.get_logger('Coin Definition')
logger.debug("Got to Coin Definition")


class BaseCoin(object):
    """
        Base class for coins. Defines the properties that need to be
        overridden.  BaseCoin uses Bitcoin as the base algorithm. For Alt coins
        override any relevant functions.
    """

    def hash_bin(self, header_bin):
        """
            The hashing algorithm that is used for proof of work
            Location: lib/template_registry.py#L232

            Args:
                heder_bin (str): The block header to be hashed.
        """
        return doublesha(header_bin)

    @property
    def calc_algo(self, nVersion, hashPrevBlock,
                  hashMerkleRoot, nTime, nBits, nNonce):
        """
            Builds Data Inside the BLOCKS
            Location: lib/halfnode.py#L250
        """
        r = []
        r.append(struct.pack("<i", nVersion))
        r.append(ser_uint256(hashPrevBlock))
        r.append(ser_uint256(hashMerkleRoot))
        r.append(struct.pack("<I", nTime))
        r.append(struct.pack("<I", nBits))
        r.append(struct.pack("<I", nNonce))
        return ''.join(r)

    @property
    def diff1(self):
        """
            The target for diff1
            Location: lib/template_registry.py#L145
        """
        return \
            0x00000000ffff0000000000000000000000000000000000000000000000000000

    @property
    def header_needs_padding(self):
        """
        The Header_Hex Needs Padding?
        Location lib/template_registry.py#L262
        """
        return False

    @property
    def block_hash_hex(self, header_bin):
        """
            The Block Hewader
            Location lib/template_registry.py#L289

            Args:
                heder_bin (str): The block header to be hashed.
        """
        return self.block_hash(header_bin)[::-1].encode('hex_codec')
