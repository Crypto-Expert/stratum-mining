import lib.logger
import lib.settings as settings
log = lib.logger.get_logger('Coin Definition')
log.debug("Got to Coin Definition")

ALGOS = {1:'ltc_scrypt', 2:None ,3:'yac_scrypt', 4:'quark_hash', 5:'xcoin_hash', 6:'algo.skeinhash.skeinhash', 7:'medcoin_hybrid', 8:'tjc_bcrypt'}
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

class algo_needed:
      def algo(self):
	  if settings.ALGORITHM == 1:
		self.algorithm = ALGOS[1]
	  elif settings.ALGORITHM == 2:
		self.algorithm = ALGOS[2]
	  elif settings.ALGORITHM == 3:
		self.algorithm = ALGOS[3] 
	  elif settings.ALGORITHM == 4:
		self.algorithm = ALGOS[4] 
	  elif settings.ALGORITHM == 5:
		self.algorithm = ALGOS[5]
	  elif settings.ALGORITHM == 6:
		self.algorithm = ALGOS[6]
	  elif settings.ALGORITHM == 7:
		self.algorithm = ALGOS[7]
	  elif settings.ALGORITHM == 8:
		self.algorithm = ALGOS[8]
	  return self.algorithm


class diff1_needed:
  def diff1(self):
    if settings.ALGORITHM == 1:
         self.DIFF1 = DIFF1[1]
    elif settings.ALGORITHM == 2:
         self.DIFF1 = DIFF1[3]
    elif settings.ALGORITHM == 3:
         self.DIFF1 = DIFF1[1] 
    elif settings.ALGORITHM == 4:
         self.DIFF1 = DIFF1[2] 
    elif settings.ALGORITHM == 5:
         self.DIFF1 = DIFF1[3]
    elif settings.ALGORITHM == 6:
         self.DIFF1 = DIFF1[3]
    elif settings.ALGORITHM == 7:
         self.DIFF1 = DIFF1[1]
    elif settings.ALGORITHM == 8:
         self.DIFF1 = DIFF1[4]
    return self.DIFF1

class header_needed:
   def header(self):
    if settings.ALGORITHM == 1 or settings.ALGORITHM == 3 or settings.ALGORITHM == 4 or settings.ALGORITHM == 7 or settings.ALGORITHM == 8:
       self.header = True
    else: self.header = False
    return self.header
