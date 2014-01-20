''' A simple wrapper for pylibmc. It can be overwritten with simple hashing if necessary '''
import lib.settings as settings
import lib.logger
log = lib.logger.get_logger('Cache')

import pylibmc
                
class Cache():
    def __init__(self):
        # Open a new connection
        self.mc = pylibmc.Client([settings.MEMCACHE_HOST + ":" + str(settings.MEMCACHE_PORT)], binary=True)
        log.info("Caching initialized")

    def set(self, key, value, time=settings.MEMCACHE_TIMEOUT):
        return self.mc.set(settings.MEMCACHE_PREFIX + str(key), value, time)

    def get(self, key):
        return self.mc.get(settings.MEMCACHE_PREFIX + str(key))

    def delete(self, key):
        return self.mc.delete(settings.MEMCACHE_PREFIX + str(key))

    def exists(self, key):
        return str(key) in self.mc.get(settings.MEMCACHE_PREFIX + str(key))
