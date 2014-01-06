import struct
import lib.logger
log = lib.logger.get_logger('extronance')

class ExtranonceCounter(object):
    '''Implementation of a counter producing
       unique extranonce across all pool instances.
       This is just dumb "quick&dirty" solution,
       but it can be changed at any time without breaking anything.'''       

    def __init__(self, instance_id):
        log.debug("Got to Extronance Counter")
        if instance_id < 0 or instance_id > 31:
            raise Exception("Current ExtranonceCounter implementation needs an instance_id in <0, 31>.")
        log.debug("Got To Extronance")

        # Last 5 most-significant bits represents instance_id
        # The rest is just an iterator of jobs.
        self.counter = instance_id << 27
        self.size = struct.calcsize('>L')
        
    def get_size(self):
        '''Return expected size of generated extranonce in bytes'''
        return self.size
    
    def get_new_bin(self):
        self.counter += 1
        return struct.pack('>L', self.counter)
        
