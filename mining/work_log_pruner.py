from time import sleep, time
import traceback
import lib.logger
log = lib.logger.get_logger('work_log_pruner')

def _WorkLogPruner_I(wl):
    now = time()
    pruned = 0
    for username in wl:
        userwork = wl[username]
        for wli in tuple(userwork.keys()):
            if now > userwork[wli][2] + 120:
                del userwork[wli]
                pruned += 1
    log.info('Pruned %d jobs' % (pruned,))

def WorkLogPruner(wl):
    while True:
        try:
            sleep(60)
            _WorkLogPruner_I(wl)
        except:
            log.debug(traceback.format_exc())
