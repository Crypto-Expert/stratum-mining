'''
This is example configuration for Stratum server.
Please rename it to config.py and fill correct values.

This is already setup with sane values for solomining.
You NEED to set the parameters in BASIC SETTINGS
'''
#********************* Config Version ***************
CONFIG_VERSION = 0.1
# ******************** BASIC SETTINGS ***************
# These are the MUST BE SET parameters!

CENTRAL_WALLET = 'set_valid_addresss_in_config!'                # Local coin address where money goes

COINDAEMON_TRUSTED_HOST = 'localhost'
COINDAEMON_TRUSTED_PORT = 8332
COINDAEMON_TRUSTED_USER = 'user'
COINDAEMON_TRUSTED_PASSWORD = 'password'                        
ALGORITHM = 1 
# Algorithm Array is as follows:
# Scrypt = 1
# SHA256 = 2(none)
# YAC = 3
# Quark = 4
# X11 = 5
# Skein = 6
# HybridSHA256 = 7
# Adding a new algo is as simple as editing lib/coindefinition.py and adding the algorithm to the array 
COINDAEMON_TX = False         # For Coins which support TX Messages please enter yes in the TX selection

# ******************** BASIC SETTINGS ***************
# Backup Coin Daemon address's (consider having at least 1 backup)
# You can have up to 99

#COINDAEMON_TRUSTED_HOST_1 = 'localhost'
#COINDAEMON_TRUSTED_PORT_1 = 8332
#COINDAEMON_TRUSTED_USER_1 = 'user'
#COINDAEMON_TRUSTED_PASSWORD_1 = 'somepassword'

#COINDAEMON_TRUSTED_HOST_2 = 'localhost'
#COINDAEMON_TRUSTED_PORT_2 = 8332
#COINDAEMON_TRUSTED_USER_2 = 'user'
#COINDAEMON_TRUSTED_PASSWORD_2 = 'somepassword'

# ******************** GENERAL SETTINGS ***************
# Set process name of twistd, much more comfortable if you run multiple processes on one machine
STRATUM_MINING_PROCESS_NAME= 'twistd-stratum-mining'


# Enable some verbose debug (logging requests and responses).
DEBUG = False

# Destination for application logs, files rotated once per day.
LOGDIR = 'log/'

# Main application log file.
LOGFILE = None      # eg. 'stratum.log'
LOGLEVEL = 'DEBUG'
# Logging Rotation can be enabled with the following settings
# It if not enabled here, you can set up logrotate to rotate the files. 
# For built in log rotation set LOG_ROTATION = True and configure the variables
LOG_ROTATION = True
LOG_SIZE = 10485760 # Rotate every 10M
LOG_RETENTION = 10 # Keep 10 Logs

# How many threads use for synchronous methods (services).
# 30 is enough for small installation, for real usage
# it should be slightly more, say 100-300.
THREAD_POOL_SIZE = 300

# ******************** TRANSPORTS *********************
# Hostname or external IP to expose
HOSTNAME = 'localhost'

# Disable the example service
ENABLE_EXAMPLE_SERVICE = False

# Port used for Socket transport. Use 'None' for disabling the transport.
LISTEN_SOCKET_TRANSPORT = 3333
# Port used for HTTP Poll transport. Use 'None' for disabling the transport
LISTEN_HTTP_TRANSPORT = None
# Port used for HTTPS Poll transport
LISTEN_HTTPS_TRANSPORT = None
# Port used for WebSocket transport, 'None' for disabling WS
LISTEN_WS_TRANSPORT = None
# Port used for secure WebSocket, 'None' for disabling WSS
LISTEN_WSS_TRANSPORT = None

# Salt used for Block Notify Password
PASSWORD_SALT = 'some_crazy_string'

# ******************** Database  *********************
DATABASE_DRIVER = 'mysql'       # Options: none, sqlite, postgresql or mysql
DATABASE_EXTEND = False         # SQLite and PGSQL Only!

# SQLite
DB_SQLITE_FILE = 'pooldb.sqlite'
# Postgresql
DB_PGSQL_HOST = 'localhost'
DB_PGSQL_DBNAME = 'pooldb'
DB_PGSQL_USER = 'pooldb'
DB_PGSQL_PASS = '**empty**'
DB_PGSQL_SCHEMA = 'public'
# MySQL
DB_MYSQL_HOST = 'localhost'
DB_MYSQL_DBNAME = 'pooldb'
DB_MYSQL_USER = 'pooldb'
DB_MYSQL_PASS = '**empty**'
DB_MYSQL_PORT = 3306            # Default port for MySQL

# ******************** Adv. DB Settings *********************
#  Don't change these unless you know what you are doing

DB_LOADER_CHECKTIME = 15        # How often we check to see if we should run the loader
DB_LOADER_REC_MIN = 10          # Min Records before the bulk loader fires
DB_LOADER_REC_MAX = 50          # Max Records the bulk loader will commit at a time
DB_LOADER_FORCE_TIME = 300      # How often the cache should be flushed into the DB regardless of size.
DB_STATS_AVG_TIME = 300         # When using the DATABASE_EXTEND option, average speed over X sec
                                # Note: this is also how often it updates
DB_USERCACHE_TIME = 600         # How long the usercache is good for before we refresh

# ******************** Pool Settings *********************

# User Auth Options
USERS_AUTOADD = False           # Automatically add users to database when they connect.
                                # This basically disables User Auth for the pool.
USERS_CHECK_PASSWORD = False    # Check the workers password? (Many pools don't)

# Transaction Settings
COINBASE_EXTRAS = '/stratumPool/'           # Extra Descriptive String to incorporate in solved blocks
ALLOW_NONLOCAL_WALLET = False               # Allow valid, but NON-Local wallet's

# Coin Daemon communication polling settings (In Seconds)
PREVHASH_REFRESH_INTERVAL = 5   # How often to check for new Blocks
                                #   If using the blocknotify script (recommended) set = to MERKLE_REFRESH_INTERVAL
                                #   (No reason to poll if we're getting pushed notifications)
MERKLE_REFRESH_INTERVAL = 60    # How often check memorypool
                                #   How often to check for new transactions to be added to the block
                                #   This effectively resets the template and incorporates new transactions.
                                #   This should be "slow"

INSTANCE_ID = 31                # Used for extranonce and needs to be 0-31

# ******************** Pool Difficulty Settings *********************
VDIFF_X2_TYPE = True            # Powers of 2 e.g. 2,4,8,16,32,64,128,256,512,1024
VDIFF_FLOAT = False             # Use float difficulty

# Pool Target (Base Difficulty)
POOL_TARGET = 32                # Pool-wide difficulty target int >= 1

# Variable Difficulty Enable
VARIABLE_DIFF = True            # Master variable difficulty enable

# Variable diff tuning variables
#VARDIFF will start at the POOL_TARGET. It can go as low as the VDIFF_MIN and as high as min(VDIFF_MAX or coindaemons difficulty)
USE_COINDAEMON_DIFF = False     # Set the maximum difficulty to the coindaemon difficulty. 
DIFF_UPDATE_FREQUENCY = 86400   # How often to check coindaemon difficulty. Should be less than coin difficulty retarget time
VDIFF_MIN_TARGET = 16           # Minimum target difficulty 
VDIFF_MAX_TARGET = 1024         # Maximum target difficulty 
VDIFF_TARGET_TIME = 15          # Target time per share (i.e. try to get 1 share per this many seconds)
VDIFF_RETARGET_TIME = 120       # How often the miners difficulty changes if appropriate
VDIFF_VARIANCE_PERCENT = 30     # Allow average time to very this % from target without retarget

# Allow external setting of worker difficulty, checks pool_worker table datarow[6] position for target difficulty
# if present or else defaults to pool target, over rides all other difficulty settings, no checks are made
# for min or max limits this should be done by your front end software
ALLOW_EXTERNAL_DIFFICULTY = False 

#### Advanced Option ##### 
# For backwards compatibility, we send the scrypt hash to the solutions column in the shares table 
# For block confirmation, we have an option to send the block hash in 
# Please make sure your front end is compatible with the block hash in the solutions table. 
# For People using the MPOS frontend enabling this is recommended. It allows the frontend to compare the block hash to the coin daemon reducing the likelihood of missing share error's for blocks
SOLUTION_BLOCK_HASH = True      # If enabled, enter the block hash. If false enter the scrypt/sha hash into the shares table 

#Pass scrypt hash to submit block check.
#Use if submit block is returning errors and marking submitted blocks invalid upstream, but the submitted blocks are being a accepted by the coin daemon into the block chain.
BLOCK_CHECK_SCRYPT_HASH = False

# ******************** Worker Ban Options *********************
ENABLE_WORKER_BANNING = True    # Enable/disable temporary worker banning 
WORKER_CACHE_TIME = 600         # How long the worker stats cache is good before we check and refresh
WORKER_BAN_TIME = 300           # How long we temporarily ban worker
INVALID_SHARES_PERCENT = 50     # Allow average invalid shares vary this % before we ban

# ******************** E-Mail Notification Settings *********************
NOTIFY_EMAIL_TO = ''                                            # Where to send Start/Found block notifications
NOTIFY_EMAIL_TO_DEADMINER = ''                                  # Where to send dead miner notifications
NOTIFY_EMAIL_FROM = 'root@localhost'                            # Sender address
NOTIFY_EMAIL_SERVER = 'localhost'                               # E-Mail sender
NOTIFY_EMAIL_USERNAME = ''                                      # E-Mail server SMTP logon
NOTIFY_EMAIL_PASSWORD = ''
NOTIFY_EMAIL_USETLS = True

# ******************** Memcache Settings *********************
# Memcahce is a requirement. Enter the settings below
MEMCACHE_HOST = "localhost"     # Hostname or IP that runs memcached
MEMCACHE_PORT = 11211           # Port
MEMCACHE_TIMEOUT = 900          # Key timeout
MEMCACHE_PREFIX = "stratum_"    # Prefix for keys
