import lib.logger
import lib.settings as settings
log = lib.logger.get_logger('Coin Definition')
log.debug("Got to Coin Definition")
from algo import *

ALGOS = {1:'ltc_scrypt', 2:None ,3:'yac_scrypt', 4:'quark_hash', 5:'x11_hash', 6:'algo.skeinhash.skeinhash', 7:'medcoin_hybrid', 8:'tjc_bcrypt'}
DIFF1 = {1:0x0000ffff00000000000000000000000000000000000000000000000000000000, 2:0x000000ffff000000000000000000000000000000000000000000000000000000, 3:0x00000000ffff0000000000000000000000000000000000000000000000000000, 4:0x001fff0000000000000000000000000000000000000000000000000000000000}
# Algorithm Array is as follows:
# Scrypt = 1
# SHA256 = 2(none)
# YAC = 3
# Quark = 4
# X11 = 5
# Skein = 6
# HybridSHA256 = 7
# tjcoin = 8
# Adding a new algo is as simple as editing lib/coindefinition.py and adding the algorithm to the array 
class algo:
      def settings(self):
	if settings.ALGORITHM == 1:
	   import ScryptCoin
	   self.settings = ScryptCoin
	return self.settings
	   

