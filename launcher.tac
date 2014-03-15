# Run me with "twistd -ny launcher.tac -l -"

# Add conf directory to python path.
# Configuration file is standard python module.
import os, sys
STRATUM_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path = [
    STRATUM_ROOT,
    os.path.join(STRATUM_ROOT, 'conf'),
    os.path.join(STRATUM_ROOT, 'externals', 'stratum-mining-proxy')
] + sys.path

from twisted.internet import defer
from twisted.application.service import Application, IProcess
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

# Run listening when mining service is ready
on_startup = defer.Deferred()

import stratum
import lib.settings as settings

# Bootstrap Stratum framework
application = stratum.setup(on_startup)


# set up logfile so it's relative to stratum directory
logfile = DailyLogFile("twisted.log", settings.STRATUM_ROOT)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)

IProcess(application).processName = settings.STRATUM_MINING_PROCESS_NAME

# Load mining service into stratum framework
import mining

from mining.interfaces import Interfaces
from mining.interfaces import WorkerManagerInterface, TimestamperInterface, \
                            ShareManagerInterface, ShareLimiterInterface

if settings.VARIABLE_DIFF == True:
    from mining.basic_share_limiter import BasicShareLimiter
    Interfaces.set_share_limiter(BasicShareLimiter())
else:
    from mining.interfaces import ShareLimiterInterface
    Interfaces.set_share_limiter(ShareLimiterInterface())

Interfaces.set_share_manager(ShareManagerInterface())
Interfaces.set_worker_manager(WorkerManagerInterface())
Interfaces.set_timestamper(TimestamperInterface())

mining.setup(on_startup)
