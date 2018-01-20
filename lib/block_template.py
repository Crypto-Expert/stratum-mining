import StringIO
import binascii
import struct
import lib.logger
import util
import merkletree
import halfnode
from coinbasetx import CoinbaseTransaction
from Crypto.Hash import SHA256 
log = lib.logger.get_logger('block_template')


# Remove dependency to settings, coinbase extras should be
# provided from coinbaser
import settings

witness_nonce = b'\0' * 0x20
witness_magic = b'\xaa\x21\xa9\xed'

class TxBlob(object):
    def __init__(self):
        self.data = ''
    def serialize(self):
       return self.data
    def deserialize(self, data):
       self.data = data

class BlockTemplate(halfnode.CBlock):
    '''Template is used for generating new jobs for clients.
    Let's iterate extranonce1, extranonce2, ntime and nonce
    to find out valid coin block!'''
    
    coinbase_transaction_class = CoinbaseTransaction
    
    def __init__(self, timestamper, coinbaser, job_id):
        log.debug("Got To  Block_template.py")
        log.debug("Got To Block_template.py")
        super(BlockTemplate, self).__init__()
        
        self.job_id = job_id 
        self.timestamper = timestamper
        self.coinbaser = coinbaser
        
        self.prevhash_bin = '' # reversed binary form of prevhash
        self.prevhash_hex = ''
        self.timedelta = 0
        self.curtime = 0
        self.target = 0
        self.witness = 0
        #self.coinbase_hex = None 
        self.merkletree = None
                
        self.broadcast_args = []
        
        # List of 4-tuples (extranonce1, extranonce2, ntime, nonce)
        # registers already submitted and checked shares
        # There may be registered also invalid shares inside!
        self.submits = [] 
                
    def fill_from_rpc(self, data):
        '''Convert getblocktemplate result into BlockTemplate instance'''
        
        commitment = None
        nTime = data['curtime'] if data.has_key('curtime') else None

        if settings.COINDAEMON_HAS_SEGWIT:
            txids = [] 
            hashes = [None] + [ util.ser_uint256(int(t['hash'], 16)) for t in data['transactions'] ]
            try:
                txids = [None] + [ util.ser_uint256(int(t['txid'], 16)) for t in data['transactions'] ]
                mt = merkletree.MerkleTree(txids)
            except KeyError:
                mt = merkletree.MerkleTree(hashes)

            wmt = merkletree.MerkleTree(hashes).withFirst(binascii.unhexlify('0000000000000000000000000000000000000000000000000000000000000000'))
            self.witness = SHA256.new(SHA256.new(wmt + witness_nonce).digest()).digest()
            commitment = b'\x6a' + struct.pack(">b", len(self.witness) + len(witness_magic)) + witness_magic + self.witness
            try:
                default_witness = data['default_witness_commitment']
                commitment_check = binascii.unhexlify(default_witness)
                if(commitment != commitment_check):
                    print("calculated witness does not match supplied one! This block probably will not be accepted!")
                    commitment = commitment_check
            except KeyError:
                 pass
            self.witness = commitment[6:]
        else:
            txhashes = [None] + [ util.ser_uint256(int(t['hash'], 16)) for t in data['transactions'] ]
            mt = merkletree.MerkleTree(txhashes)

        coinbase = CoinbaseTransaction(self.timestamper, self.coinbaser, data['coinbasevalue'],
                                              data['coinbaseaux']['flags'], data['height'],
                                              commitment, settings.COINBASE_EXTRAS, nTime)

        self.height = data['height']
        self.nVersion = data['version']
        self.hashPrevBlock = int(data['previousblockhash'], 16)
        self.nBits = int(data['bits'], 16)
        self.hashMerkleRoot = 0
        self.nTime = 0
        self.nNonce = 0
        self.vtx = [ coinbase, ]
        
        for tx in data['transactions']:
            t = TxBlob()
            t.deserialize(binascii.unhexlify(tx['data']))
            self.vtx.append(t)
            
        self.curtime = data['curtime']
        self.timedelta = self.curtime - int(self.timestamper.time()) 
        self.merkletree = mt
        self.target = util.uint256_from_compact(self.nBits)
        
        # Reversed prevhash
        self.prevhash_bin = binascii.unhexlify(util.reverse_hash(data['previousblockhash']))
        self.prevhash_hex = "%064x" % self.hashPrevBlock
        
        self.broadcast_args = self.build_broadcast_args()
                
    def register_submit(self, extranonce1, extranonce2, ntime, nonce):
        '''Client submitted some solution. Let's register it to
        prevent double submissions.'''
        
        t = (extranonce1, extranonce2, ntime, nonce)
        if t not in self.submits:
            self.submits.append(t)
            return True
        return False
            
    def build_broadcast_args(self):
        '''Build parameters of mining.notify call. All clients
        may receive the same params, because they include
        their unique extranonce1 into the coinbase, so every
        coinbase_hash (and then merkle_root) will be unique as well.'''
        job_id = self.job_id
        prevhash = binascii.hexlify(self.prevhash_bin)
        (coinb1, coinb2) = [ binascii.hexlify(x) for x in self.vtx[0]._serialized ]
        merkle_branch = [ binascii.hexlify(x) for x in self.merkletree._steps ]
        version = binascii.hexlify(struct.pack(">i", self.nVersion))
        nbits = binascii.hexlify(struct.pack(">I", self.nBits))
        ntime = binascii.hexlify(struct.pack(">I", self.curtime))
        clean_jobs = True
        
        return (job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs)

    def serialize_coinbase(self, extranonce1, extranonce2):
        '''Serialize coinbase with given extranonce1 and extranonce2
        in binary form'''
        (part1, part2) = self.vtx[0]._serialized
        return part1 + extranonce1 + extranonce2 + part2
    
    def check_ntime(self, ntime):
        '''Check for ntime restrictions.'''
        if ntime < self.curtime:
            return False
        
        if ntime > (self.timestamper.time() + 7200):
            # Be strict on ntime into the near future
            # may be unnecessary
            return False
        
        return True

    def serialize_header(self, merkle_root_int, ntime_bin, nonce_bin):
        '''Serialize header for calculating block hash'''
        r  = struct.pack(">i", self.nVersion)
        r += self.prevhash_bin
        r += util.ser_uint256_be(merkle_root_int)
        r += ntime_bin
        r += struct.pack(">I", self.nBits)
        r += nonce_bin    
        return r       

    def finalize(self, merkle_root_int, extranonce1_bin, extranonce2_bin, ntime, nonce):
        '''Take all parameters required to compile block candidate.
        self.is_valid() should return True then...'''
        
        self.hashMerkleRoot = merkle_root_int
        self.nTime = ntime
        self.nNonce = nonce
        self.vtx[0].set_extranonce(extranonce1_bin + extranonce2_bin)        
        self.sha256 = None # We changed block parameters, let's reset sha256 cache

    def is_valid(self):
        self.calc_hash()
        target = util.uint256_from_compact(self.nBits)
        if self.sha256 > self.target:
            return False
        hashes = []
        hashes.append(b'\0' * 0x20)
        for tx in self.vtx[1:]:
            hashes.append(SHA256.new(SHA256.new(tx.serialize()).digest()).digest())
        while len(hashes) > 1:
            newhashes = []
            for i in xrange(0, len(hashes), 2):
                i2 = min(i+1, len(hashes)-1)
                newhashes.append(SHA256.new(SHA256.new(hashes[i] + hashes[i2]).digest()).digest())
            hashes = newhashes
        calcwitness = SHA256.new(SHA256.new(hashes[0] + witness_nonce).digest()).digest()
        if calcwitness != self.witness:
            return False
        return True 
