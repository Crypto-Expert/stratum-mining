import lib.logger
log = lib.logger.get_logger('Coin Definition')
log.debug("Got to Coin Definition")

ALGOS = ['sha256d','ltc_scrypt','yac_scrypt','quark_hash','x11_hash']

ALGORITHM = 1 
TX_MESSAGES = True
# Algorithm Array is as follows:
# Scrypt = 1
# SHA256 = 2 
# YAC = 3
# Quark = 4
# Skein = 5
# Adding a new algo is as simple as editing lib/coindefinition.py and adding the algorithm to there
