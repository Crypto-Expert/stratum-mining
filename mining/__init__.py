from service import MiningService
from subscription import MiningSubscription
from twisted.internet import defer
from twisted.internet.error import ConnectionRefusedError
import time
import simplejson as json
from twisted.internet import reactor
import threading
from mining.work_log_pruner import WorkLogPruner

@defer.inlineCallbacks
def setup(on_startup):
    '''Setup mining service internal environment.
    You should not need to change this. If you
    want to use another Worker manager or Share manager,
    you should set proper reference to Interfaces class
    *before* you call setup() in the launcher script.'''
    
    import lib.settings as settings
        
    # Get logging online as soon as possible
    import lib.logger
    log = lib.logger.get_logger('mining')

    from interfaces import Interfaces
    
    from lib.block_updater import BlockUpdater
    from lib.template_registry import TemplateRegistry
    from lib.bitcoin_rpc_manager import BitcoinRPCManager
    from lib.block_template import BlockTemplate
    from lib.coinbaser import SimpleCoinbaser
    
    bitcoin_rpc = BitcoinRPCManager()
    
    # Check litecoind
    #         Check we can connect (sleep)
    # Check the results:
    #         - getblocktemplate is avalible        (Die if not)
    #         - we are not still downloading the blockchain        (Sleep)
    log.info("Connecting to litecoind...")
    while True:
        try:
            result = (yield bitcoin_rpc.check_submitblock())
            if result == True:
                log.info("Found submitblock")
            elif result == False:
                log.info("Did not find submitblock")
            else:
                log.info("unknown submitblock result")
        except ConnectionRefusedError, e:
            log.error("Connection refused while trying to connect to the coind (are your COIND_* settings correct?)")
            reactor.stop()
            break

        except Exception, e:
            log.debug(str(e))

        try:
            result = (yield bitcoin_rpc.getblocktemplate())
            if isinstance(result, dict):
                # litecoind implements version 1 of getblocktemplate
                if result['version'] >= 1:
                    result = (yield bitcoin_rpc.getdifficulty())
                    if isinstance(result,dict):
                        if 'proof-of-stake' in result: 
                            settings.COINDAEMON_Reward = 'POS'
                            log.info("Coin detected as POS")
                            break
                    else:
                        settings.COINDAEMON_Reward = 'POW'
                        log.info("Coin detected as POW")
                        break
                else:
                    log.error("Block Version mismatch: %s" % result['version'])


        except ConnectionRefusedError, e:
            log.error("Connection refused while trying to connect to the coind (are your COIND_* settings correct?)")
            reactor.stop()
            break

        except Exception, e:
            if isinstance(e[2], str):
                try:
                    if isinstance(json.loads(e[2])['error']['message'], str):
                        error = json.loads(e[2])['error']['message']
                    if error == "Method not found":
                        log.error("CoinD does not support getblocktemplate!!! (time to upgrade.)")
                        reactor.stop()
                    elif "downloading blocks" in error:
                        log.error("CoinD downloading blockchain... will check back in 30 sec")
                        time.sleep(29)
                    else:
                        log.error("Coind Error: %s", error)
                except ValueError:
                    log.error("Failed Connect(HTTP 500 or Invalid JSON), Check Username and Password!")
                    reactor.stop()
        time.sleep(1)  # If we didn't get a result or the connect failed
        
    log.info('Connected to the coind - Begining to load Address and Module Checks!')

    # Start the coinbaser
    coinbaser = SimpleCoinbaser(bitcoin_rpc, getattr(settings, 'CENTRAL_WALLET'))
    (yield coinbaser.on_load)
    
    registry = TemplateRegistry(BlockTemplate,
                                coinbaser,
                                bitcoin_rpc,
                                getattr(settings, 'INSTANCE_ID'),
                                MiningSubscription.on_template,
                                Interfaces.share_manager.on_network_block)
    
    # Template registry is the main interface between Stratum service
    # and pool core logic
    Interfaces.set_template_registry(registry)
    
    # Set up polling mechanism for detecting new block on the network
    # This is just failsafe solution when -blocknotify
    # mechanism is not working properly    
    BlockUpdater(registry, bitcoin_rpc)

    prune_thr = threading.Thread(target=WorkLogPruner, args=(Interfaces.worker_manager.job_log,))
    prune_thr.daemon = True
    prune_thr.start()
    
    log.info("MINING SERVICE IS READY")
    on_startup.callback(True)





