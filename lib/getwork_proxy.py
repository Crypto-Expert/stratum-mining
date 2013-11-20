import stratum.logger
log = stratum.logger.get_logger('Getwork Proxy')

from stratum import settings
from stratum.socket_transport import SocketTransportClientFactory
            
from twisted.internet import reactor, defer
from twisted.web import server

from mining_libs import getwork_listener
from mining_libs import client_service
from mining_libs import jobs
from mining_libs import worker_registry
from mining_libs import version

class Site(server.Site):
    def log(self, request):
	pass

def on_shutdown(f):
    log.info("Shutting down proxy...")
    f.is_reconnecting = False # Don't let stratum factory to reconnect again
    
@defer.inlineCallbacks
def on_connect(f, workers, job_registry):
    log.info("Connected to Stratum pool at %s:%d" % f.main_host)
    
    # Hook to on_connect again
    f.on_connect.addCallback(on_connect, workers, job_registry)
    
    # Every worker have to re-autorize
    workers.clear_authorizations() 
        
    # Subscribe for receiving jobs
    log.info("Subscribing for mining jobs")
    (_, extranonce1, extranonce2_size) = (yield f.rpc('mining.subscribe', []))
    job_registry.set_extranonce(extranonce1, extranonce2_size)
    
    defer.returnValue(f)
     
def on_disconnect(f, workers, job_registry):
    log.info("Disconnected from Stratum pool at %s:%d" % f.main_host)
    f.on_disconnect.addCallback(on_disconnect, workers, job_registry)
    
    # Reject miners because we don't give a *job :-)
    workers.clear_authorizations() 
    return f              

@defer.inlineCallbacks
def GetworkProxy_main(cb):
    log.info("Stratum proxy version %s Connecting to Pool..." % version.VERSION)
        
    # Connect to Stratum pool
    f = SocketTransportClientFactory(settings.HOSTNAME, settings.LISTEN_SOCKET_TRANSPORT,
                debug=False, proxy=None, event_handler=client_service.ClientMiningService)
    
    job_registry = jobs.JobRegistry(f, cmd='', no_midstate=settings.GW_DISABLE_MIDSTATE, real_target=settings.GW_SEND_REAL_TARGET)
    client_service.ClientMiningService.job_registry = job_registry
    client_service.ClientMiningService.reset_timeout()
    
    workers = worker_registry.WorkerRegistry(f)
    f.on_connect.addCallback(on_connect, workers, job_registry)
    f.on_disconnect.addCallback(on_disconnect, workers, job_registry)
    
    # Cleanup properly on shutdown
    reactor.addSystemEventTrigger('before', 'shutdown', on_shutdown, f)

    # Block until proxy connects to the pool
    yield f.on_connect
    
    # Setup getwork listener
    gw_site = Site(getwork_listener.Root(job_registry, workers,
		stratum_host=settings.HOSTNAME, stratum_port=settings.LISTEN_SOCKET_TRANSPORT,
		custom_lp=False, custom_stratum=False,
		custom_user=False, custom_password=False
		))
    gw_site.noisy = False
    reactor.listenTCP(settings.GW_PORT, gw_site, interface='0.0.0.0')
    
    log.info("Getwork Proxy is online, Port: %d" % (settings.GW_PORT))

def GetworkProxy(start_event):
    start_event.addCallback(GetworkProxy_main)

