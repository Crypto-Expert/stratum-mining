import time
import hashlib
import lib.settings as settings
import lib.logger
log = lib.logger.get_logger('DB_Mysql')

import MySQLdb
import DB_Mysql
                
class DB_Mysql_Vardiff(DB_Mysql.DB_Mysql):
    def __init__(self):
        DB_Mysql.DB_Mysql.__init__(self)
    
    def import_shares(self, data):
        # Data layout
        # 0: worker_name, 
        # 1: block_header, 
        # 2: block_hash, 
        # 3: difficulty, 
        # 4: timestamp, 
        # 5: is_valid, 
        # 6: ip, 
        # 7: self.block_height, 
        # 8: self.prev_hash,
        # 9: invalid_reason, 
        # 10: share_diff

        log.debug("Importing Shares")
        checkin_times = {}
        total_shares = 0
        best_diff = 0
        
        for k, v in enumerate(data):
            # for database compatibility we are converting our_worker to Y/N format
            if v[5]:
                v[5] = 'Y'
            else:
                v[5] = 'N'

            self.execute(
                """
                INSERT INTO `shares`
                (time, rem_host, username, our_result, 
                  upstream_result, reason, solution, difficulty)
                VALUES 
                (FROM_UNIXTIME(%(time)s), %(host)s, 
                  %(uname)s, 
                  %(lres)s, 'N', %(reason)s, %(solution)s, %(difficulty)s)
                """,
                {
                    "time": v[4], 
                    "host": v[6], 
                    "uname": v[0], 
                    "lres": v[5], 
                    "reason": v[9],
                    "solution": v[2],
                    "difficulty": v[3]
                }
            )

            self.dbh.commit()
    
    def found_block(self, data):
        # for database compatibility we are converting our_worker to Y/N format
        if data[5]:
            data[5] = 'Y'
        else:
            data[5] = 'N'

        # Check for the share in the database before updating it
        # Note: We can't use DUPLICATE KEY because solution is not a key

        self.execute(
            """
            Select `id` from `shares`
            WHERE `solution` = %(solution)s
            LIMIT 1
            """,
            {
                "solution": data[2]
            }
        )

        shareid = self.dbc.fetchone()

        if shareid[0] > 0:
            # Note: difficulty = -1 here
            self.execute(
                """
                UPDATE `shares`
                SET `upstream_result` = %(result)s
                WHERE `solution` = %(solution)s
                AND `id` = %(id)s
                LIMIT 1
                """,
                {
                    "result": data[5], 
                    "solution": data[2],
                    "id": shareid[0]
                }
            )
            
            self.dbh.commit()
        else:
            self.execute(
                """
                INSERT INTO `shares`
                (time, rem_host, username, our_result, 
                  upstream_result, reason, solution)
                VALUES 
                (FROM_UNIXTIME(%(time)s), %(host)s, 
                  %(uname)s, 
                  %(lres)s, %(result)s, %(reason)s, %(solution)s)
                """,
                {
                    "time": v[4], 
                    "host": v[6], 
                    "uname": v[0], 
                    "lres": v[5], 
                    "result": v[5], 
                    "reason": v[9],
                    "solution": v[2]
                }
            )

            self.dbh.commit()


    def update_worker_diff(self, username, diff):
        log.debug("Setting difficulty for %s to %s", username, diff)
        
        self.execute(
            """
            UPDATE `pool_worker`
            SET `difficulty` = %(diff)s
            WHERE `username` = %(uname)s
            """,
            {
                "uname": username, 
                "diff": diff
            }
        )
        
        self.dbh.commit()
    
    def clear_worker_diff(self):
        log.debug("Resetting difficulty for all workers")
        
        self.execute(
            """
            UPDATE `pool_worker`
            SET `difficulty` = 0
            """
        )
        
        self.dbh.commit()


    def get_workers_stats(self):
        self.execute(
            """
            SELECT `username`, `speed`, `last_checkin`, `total_shares`,
              `total_rejects`, `total_found`, `alive`, `difficulty`
            FROM `pool_worker`
            WHERE `id` > 0
            """
        )
        
        ret = {}
        
        for data in self.dbc.fetchall():
            ret[data[0]] = {
                "username": data[0],
                "speed": int(data[1]),
                "last_checkin": time.mktime(data[2].timetuple()),
                "total_shares": int(data[3]),
                "total_rejects": int(data[4]),
                "total_found": int(data[5]),
                "alive": True if data[6] is 1 else False,
                "difficulty": float(data[7])
            }
            
        return ret


