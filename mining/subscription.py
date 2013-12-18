from stratum.pubsub import Pubsub, Subscription
from mining.interfaces import Interfaces

import lib.settings as settings
import lib.logger
log = lib.logger.get_logger('subscription')

class MiningSubscription(Subscription):
    '''This subscription object implements
    logic for broadcasting new jobs to the clients.'''
    
    event = 'mining.notify'
    
    @classmethod
    def on_template(cls, is_new_block):
        '''This is called when TemplateRegistry registers
           new block which we have to broadcast clients.'''
        
        start = Interfaces.timestamper.time()
        clean_jobs = is_new_block
        
        (job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, _) = \
            Interfaces.template_registry.get_last_broadcast_args()

        # Push new job to subscribed clients
        for subscription in Pubsub.iterate_subscribers(cls.event):
            try:
                if subscription != None:
                    session = subscription.connection_ref().get_session()
                    session.setdefault('authorized', {})
                    if session['authorized'].keys():
                        worker_name = session['authorized'].keys()[0]
                        difficulty = session['difficulty']
                        work_id = Interfaces.worker_manager.register_work(worker_name, job_id, difficulty)             
                        subscription.emit_single(work_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs)
                    else:
                        subscription.emit_single(job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs)
            except Exception as e:
                log.exception("Error broadcasting work to client %s" % str(e))
                pass
        
        cnt = Pubsub.get_subscription_count(cls.event)
        log.info("BROADCASTED to %d connections in %.03f sec" % (cnt, (Interfaces.timestamper.time() - start)))
        
    def _finish_after_subscribe(self, result):
        '''Send new job to newly subscribed client'''
        try:        
            (job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, _) = \
                        Interfaces.template_registry.get_last_broadcast_args()
        except Exception:
            log.error("Template not ready yet")
            return result
        
        # Force set higher difficulty
        self.connection_ref().rpc('mining.set_difficulty', [settings.POOL_TARGET, ], is_notification=True)
        # self.connection_ref().rpc('client.get_version', [])
        
        # Force client to remove previous jobs if any (eg. from previous connection)
        clean_jobs = True
        self.emit_single(job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, True)
        
        return result
                
    def after_subscribe(self, *args):
        '''This will send new job to the client *after* he receive subscription details.
        on_finish callback solve the issue that job is broadcasted *during*
        the subscription request and client receive messages in wrong order.'''
        self.connection_ref().on_finish.addCallback(self._finish_after_subscribe)

