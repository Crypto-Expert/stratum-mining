import util
from twisted.internet import defer

import settings

import lib.logger
log = lib.logger.get_logger('coinbaser')

# TODO: Add on_* hooks in the app
    
class SimpleCoinbaser(object):
    '''This very simple coinbaser uses a constant coin address
    for all generated blocks.'''
    
    def __init__(self, bitcoin_rpc, address):
        # Fire callback when coinbaser is ready
        self.on_load = defer.Deferred()
        
        self.address = address
        self.is_valid = False # We need to check if pool can use this address
        
        self.bitcoin_rpc = bitcoin_rpc
        self._validate()

    def _validate(self):
        d = self.bitcoin_rpc.validateaddress(self.address)
        d.addCallback(self._address_check)
        d.addErrback(self._failure)
        
    def _address_check(self, result):
        if result['isvalid'] and result['ismine']:
            self.is_valid = True
            log.info("Coinbase address '%s' is valid" % self.address)
            
            if not self.on_load.called:
                self.on_load.callback(True)
	
	elif result['isvalid'] and settings.ALLOW_NONLOCAL_WALLET == True :
            self.is_valid = True
            log.warning("!!! Coinbase address '%s' is valid BUT it is not local" % self.address)
            
            if not self.on_load.called:
                self.on_load.callback(True)
                
        else:
            self.is_valid = False
            log.error("Coinbase address '%s' is NOT valid!" % self.address)
        
    def _failure(self, failure):
        log.error("Cannot validate Bitcoin address '%s'" % self.address)
        raise
    
    #def on_new_block(self):
    #    pass
    
    #def on_new_template(self):
    #    pass
    
    def get_script_pubkey(self):
        if not self.is_valid:
            # Try again, maybe the coind was down?
            self._validate()
            raise Exception("Coinbase address is not validated!")
        return util.script_to_address(self.address)    
                   
    def get_coinbase_data(self):
        return ''
