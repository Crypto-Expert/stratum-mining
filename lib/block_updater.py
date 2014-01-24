from twisted.internet import reactor, defer
import settings

import util
from mining.interfaces import Interfaces

import lib.logger
log = lib.logger.get_logger('block_updater')

class BlockUpdater(object):
    '''
        Polls upstream's getinfo() and detecting new block on the network.
        This will call registry.update_block when new prevhash appear.
        
        This is just failback alternative when something
        with ./litecoind -blocknotify will go wrong. 
    '''
    
    def __init__(self, registry, bitcoin_rpc):
        log.debug("Got To Block Updater")
        self.bitcoin_rpc = bitcoin_rpc
        self.registry = registry
        self.clock = None
        self.schedule()
                        
    def schedule(self):
        when = self._get_next_time()
        log.debug("Next prevhash update in %.03f sec" % when)
        log.debug("Merkle update in next %.03f sec" % \
                  ((self.registry.last_update + settings.MERKLE_REFRESH_INTERVAL)-Interfaces.timestamper.time()))
        self.clock = reactor.callLater(when, self.run)
        
    def _get_next_time(self):
        when = settings.PREVHASH_REFRESH_INTERVAL - (Interfaces.timestamper.time() - self.registry.last_update) % \
               settings.PREVHASH_REFRESH_INTERVAL
        return when  
                     
    @defer.inlineCallbacks
    def run(self):
        update = False
       
        try:             
            if self.registry.last_block:
                current_prevhash = "%064x" % self.registry.last_block.hashPrevBlock
            else:
                current_prevhash = None
                
            log.info("Checking for new block.")
            prevhash = util.reverse_hash((yield self.bitcoin_rpc.prevhash()))
            if prevhash and prevhash != current_prevhash:
                log.info("New block! Prevhash: %s" % prevhash)
                update = True
            
            elif Interfaces.timestamper.time() - self.registry.last_update >= settings.MERKLE_REFRESH_INTERVAL:
                log.info("Merkle update! Prevhash: %s" % prevhash)
                update = True
                
            if update:
                self.registry.update_block()

        except Exception:
            log.exception("UpdateWatchdog.run failed")
        finally:
            self.schedule()

    
