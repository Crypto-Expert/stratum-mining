'''
    Implements simple interface to a coin daemon's RPC.
'''

import simplejson as json
import base64
from twisted.internet import defer
from twisted.web import client
import time
import util
import lib.logger
import lib.settings as settings
log = lib.logger.get_logger('bitcoin_rpc')

gbt_known_rules = ["segwit"]

class BitcoinRPC(object):

    def __init__(self, host, port, username, password):
        self.bitcoin_url = 'http://%s:%d' % (host, port)
        self.credentials = base64.b64encode("%s:%s" % (username, password))
        self.headers = {
            'Content-Type': 'text/json',
            'Authorization': 'Basic %s' % self.credentials,
        }
        client.HTTPClientFactory.noisy = False
	self.has_submitblock = False

    def _call_raw(self, data):
        client.Headers
        return client.getPage(
            url=self.bitcoin_url,
            method='POST',
            headers=self.headers,
            postdata=data,
        )

    def _call(self, method, params):
        return self._call_raw(json.dumps({
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': '1',
            }))

    @defer.inlineCallbacks
    def check_submitblock(self):
        try:
            resp = (yield self._call('submitblock', []))
	    self.has_submitblock = True
        except Exception as e:
            if (str(e) == "404 Not Found"):
		self.has_submitblock = False
            elif (str(e) == "500 Internal Server Error"):
		self.has_submitblock = True
            else:
		self.has_submitblock = True
        finally:
              defer.returnValue(self.has_submitblock)


    @defer.inlineCallbacks
    def submitblock(self, block_hex, hash_hex, scrypt_hex):
	#try 5 times? 500 Internal Server Error could mean random error or that TX messages setting is wrong
        attempts = 0
        while True:
            attempts += 1
            if self.has_submitblock:
                try:
                    log.debug([block_hex,])
                    resp = (yield self._call('submitblock', [block_hex,]))
                    break
                except Exception as e:
                    if attempts > 4:
                        log.exception("submitblock failed. Problem Submitting block %s" % str(e))
                        log.exception("Try Enabling TX Messages in config.py!")
                        raise
            else:
                try:
                    resp = (yield self._call('getblocktemplate', [{'mode': 'submit', 'data': block_hex}]))
                    break
                except Exception as e:
                    if attempts > 4:
                        log.exception("getblocktemplate submit failed. Problem Submitting block %s" % str(e))
                        log.exception("Try Enabling TX Messages in config.py!")
                        raise

        if json.loads(resp)['result'] == None:
            # make sure the block was created.
            defer.returnValue((yield self.blockexists(hash_hex, scrypt_hex)))
        else:
            defer.returnValue(False)

    @defer.inlineCallbacks
    def getinfo(self):
         resp = (yield self._call('getinfo', []))
         defer.returnValue(json.loads(resp)['result'])

    @defer.inlineCallbacks
    def getblocktemplate(self):
        try:
            params = [{}]
            if settings.COINDAEMON_HAS_SEGWIT:
               params = [{"rules": gbt_known_rules}]
            resp = (yield self._call('getblocktemplate', params))
            defer.returnValue(json.loads(resp)['result'])
        # if internal server error try getblocktemplate without empty {} # ppcoin
        except Exception as e:
            if (str(e) == "500 Internal Server Error"):
                resp = (yield self._call('getblocktemplate', []))
                defer.returnValue(json.loads(resp)['result'])
            else:
                raise

    @defer.inlineCallbacks
    def prevhash(self):
        try:
            resp = (yield self._call('getbestblockhash', []))
            defer.returnValue(json.loads(resp)['result'])
        # if internal server error try getblocktemplate without empty {} # ppcoin
        except Exception as e:
            if (str(e) == "500 Internal Server Error"):
                resp = (yield self._call('getwork', []))
                defer.returnValue(util.reverse_hash(json.loads(resp)['result']['data'][8:72]))
            else:
                log.exception("Cannot decode prevhash %s" % str(e))
                raise

    @defer.inlineCallbacks
    def validateaddress(self, address):
        resp = (yield self._call('validateaddress', [address,]))
        defer.returnValue(json.loads(resp)['result'])

    @defer.inlineCallbacks
    def getdifficulty(self):
        resp = (yield self._call('getdifficulty', []))
        defer.returnValue(json.loads(resp)['result'])

    @defer.inlineCallbacks
    def blockexists(self, hash_hex, scrypt_hex):
        valid_hash = None
        blockheight = None
        # try both hash_hex and scrypt_hex to find block
        try:
            resp = (yield self._call('getblock', [hash_hex,]))
            result = json.loads(resp)['result']
            if "hash" in result and result['hash'] == hash_hex:
                log.debug("Block found: %s" % hash_hex)
                valid_hash = hash_hex
                if "height" in result:
                    blockheight = result['height']
                else:
                    defer.returnValue(True)
            else:
                log.info("Cannot find block for %s" % hash_hex)
                defer.returnValue(False)

        except Exception as e:
            try:
                resp = (yield self._call('getblock', [scrypt_hex,]))
                result = json.loads(resp)['result']
                if "hash" in result and result['hash'] == scrypt_hex:
                    valid_hash = scrypt_hex
                    log.debug("Block found: %s" % scrypt_hex)
                    if "height" in result:
                        blockheight = result['height']
                    else:
                        defer.returnValue(True)
                else:
                    log.info("Cannot find block for %s" % scrypt_hex)
                    defer.returnValue(False)

            except Exception as e:
                log.info("Cannot find block for hash_hex %s or scrypt_hex %s" % hash_hex, scrypt_hex)
                defer.returnValue(False)

        #after we've found the block, check the block with that height in the blockchain to see if hashes match
        try:
            log.debug("checking block hash against hash of block height: %s", blockheight)
            resp = (yield self._call('getblockhash', [blockheight,]))
            hash = json.loads(resp)['result']
            log.debug("hash of block of height %s: %s", blockheight, hash)
            if hash == valid_hash:
                log.debug("Block confirmed: hash of block matches hash of blockheight")
                defer.returnValue(True)
            else:
                log.debug("Block invisible: hash of block does not match hash of blockheight")
                defer.returnValue(False)

        except Exception as e:
            # cannot get blockhash from height; block was created, so return true
            defer.returnValue(True)
        else:
            log.info("Cannot find block for %s" % hash_hex)
            defer.returnValue(False)
