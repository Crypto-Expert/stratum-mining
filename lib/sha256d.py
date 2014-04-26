import basecoin
import lib.logger
logger = lib.logger.get_logger('SHA256Coin Definition')
logger.debug("Got to SHA256Coin Definition")
Base = basecoin.Base

class Coin(Base):
   def __init__(self):
       self.algo = None
