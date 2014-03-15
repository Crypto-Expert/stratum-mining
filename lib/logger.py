'''Simple wrapper around python's logging package'''

import os
import logging
import logging.handlers
import settings


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.setLevel(getattr(logging, settings.LOGLEVEL))

    if settings.LOGFILE is not None:
        logger.addHandler(file_handler)

    logger.debug("Logging initialized")
    return logger
    #return Logger()

if settings.DEBUG:
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(module)s.%(funcName)s # %(message)s"
    )
else:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s # %(message)s")

if settings.LOGFILE is not None:
    # Create the log folder if it does not exist
    LOGDIR = os.path.join(settings.STRATUM_ROOT, settings.LOGDIR)
    LOGPATH = os.path.join(LOGDIR, settings.LOGFILE)

    try:
        os.makedirs(LOGDIR)
    except OSError:
        pass

    # Setup log rotation if specified in the config
    if settings.LOG_ROTATION:
        file_handler = logging.handlers.RotatingFileHandler(
            LOGPATH,
            mode='a',
            maxBytes=settings.LOG_SIZE,
            backupCount=settings.LOG_RETENTION
        )
    else:
        file_handler = logging.handlers.WatchedFileHandler(
            LOGPATH
        )

    file_handler.setFormatter(fmt)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(fmt)
