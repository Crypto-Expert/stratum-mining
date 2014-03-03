import lib.logger
import lib.settings as settings
log = lib.logger.get_logger('Coin Definition')
log.debug("Got to Coin Definition")

ALGOS = ['ltc_scrypt','yac_scrypt','quark_hash','x11_hash','algo.skeinhash.skeinhash']
DIFF1 = ['0x0000ffff00000000000000000000000000000000000000000000000000000000','0x000000ffff000000000000000000000000000000000000000000000000000000','0x00000000ffff0000000000000000000000000000000000000000000000000000']
# Algorithm Array is as follows:
# Scrypt = 1
# SHA256 = 2 
# YAC = 3
# Quark = 4
# X11 = 5
# Skein = 6
# Adding a new algo is as simple as editing lib/coindefinition.py and adding the algorithm to the array 

def algo(self):
    if settings.ALGORITHM == 1:
         return ALGOS[1]
    elif settings.ALGORITHM == 2:
         return None
    elif settings.ALGORITHM == 3:
         return ALGOS[2] 
    elif settings.ALGORITHM == 4:
         return ALGOS[3] 
    elif settings.ALGORITHM == 5:
         return ALGOS[4]
    elif settings.ALGORITHM == 6:
         return ALGOS[5]
         
def diff1(self):
    if settings.ALGORITHM == 1:
         return DIFF1[1]
    elif settings.ALGORITHM == 2:
         return DIFF1[3]
    elif settings.ALGORITHM == 3:
         return DIFF1[1] 
    elif settings.ALGORITHM == 4:
         return DIFF1[2] 
    elif settings.ALGORITHM == 5:
         return DIFF1[3]
    elif settings.ALGORITHM == 6:
         return DIFF1[3]
         
def header(self):
    if settings.ALGORITHM == 1 or settings.ALGORITHM == 3 or settings.ALGORITHM == 4 
       return True
