import time
import hashlib
import lib.settings as settings
import lib.logger
log = lib.logger.get_logger('DB_Mysql')

import MySQLdb
import DB_Mysql
                
class DB_Mysql_Extended(DB_Mysql.DB_Mysql):
    def __init__(self):
        DB_Mysql.DB_Mysql.__init__(self)

    def updateStats(self, averageOverTime):
        log.debug("Updating Stats")
        # Note: we are using transactions... so we can set the speed = 0 and it doesn't take affect until we are commited.
        self.execute(
            """
            UPDATE `pool_worker`
            SET `speed` = 0, 
              `alive` = 0
            """
        );
        
        stime = '%.0f' % (time.time() - averageOverTime);
        
        self.execute(
            """
            UPDATE `pool_worker` pw
            LEFT JOIN (
                SELECT `worker`, ROUND(ROUND(SUM(`difficulty`)) * 4294967296) / %(average)s AS 'speed'
                FROM `shares`
                WHERE `time` > FROM_UNIXTIME(%(time)s)
                GROUP BY `worker`
            ) AS leJoin
            ON leJoin.`worker` = pw.`id`
            SET pw.`alive` = 1, 
              pw.`speed` = leJoin.`speed`
            WHERE pw.`id` = leJoin.`worker`
            """,
            {
                "time": stime,
                "average": int(averageOverTime) * 1000000
            }
        )
            
        self.execute(
            """
            UPDATE `pool`
            SET `value` = (
                SELECT IFNULL(SUM(`speed`), 0)
                FROM `pool_worker`
                WHERE `alive` = 1
            )
            WHERE `parameter` = 'pool_speed'
            """
        )
        
        self.dbh.commit()
    
    def archive_check(self):
        # Check for found shares to archive
        self.execute(
            """
            SELECT `time`
            FROM `shares` 
            WHERE `upstream_result` = 1
            ORDER BY `time` 
            LIMIT 1
            """
        )
        
        data = self.dbc.fetchone()
        
        if data is None or (data[0] + getattr(settings, 'ARCHIVE_DELAY')) > time.time():
            return False
        
        return data[0]

    def archive_found(self, found_time):
        self.execute(
            """
            INSERT INTO `shares_archive_found`
            SELECT s.`id`, s.`time`, s.`rem_host`, pw.`id`, s.`our_result`, 
              s.`upstream_result`, s.`reason`, s.`solution`, s.`block_num`, 
              s.`prev_block_hash`, s.`useragent`, s.`difficulty`
            FROM `shares` s 
            LEFT JOIN `pool_worker` pw
              ON s.`worker` = pw.`id`
            WHERE `upstream_result` = 1
              AND `time` <= FROM_UNIXTIME(%(time)s)
            """,
            {
                "time": found_time
            }
        )
        
        self.dbh.commit()

    def archive_to_db(self, found_time):
        self.execute(
            """
            INSERT INTO `shares_archive`
            SELECT s.`id`, s.`time`, s.`rem_host`, pw.`id`, s.`our_result`, 
              s.`upstream_result`, s.`reason`, s.`solution`, s.`block_num`, 
              s.`prev_block_hash`, s.`useragent`, s.`difficulty`
            FROM `shares` s 
            LEFT JOIN `pool_worker` pw
              ON s.`worker` = pw.`id`
            WHERE `time` <= FROM_UNIXTIME(%(time)s)
            """,
            {
                "time": found_time
            }
        )
        
        self.dbh.commit()

    def archive_cleanup(self, found_time):
        self.execute(
            """
            DELETE FROM `shares` 
            WHERE `time` <= FROM_UNIXTIME(%(time)s)
            """,
            {
                "time": found_time
            }
        )
        
        self.dbh.commit()

    def archive_get_shares(self, found_time):
        self.execute(
            """
            SELECT *
            FROM `shares` 
            WHERE `time` <= FROM_UNIXTIME(%(time)s)
            """,
            {
                "time": found_time
            }
        )
        
        return self.dbc

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
            total_shares += v[3]
            
            if v[0] in checkin_times:
                if v[4] > checkin_times[v[0]]:
                    checkin_times[v[0]]["time"] = v[4]
            else:
                checkin_times[v[0]] = {
                    "time": v[4], 
                    "shares": 0, 
                    "rejects": 0
                }

            if v[5] == True:
                checkin_times[v[0]]["shares"] += v[3]
            else:
                checkin_times[v[0]]["rejects"] += v[3]

            if v[10] > best_diff:
                best_diff = v[10]

            self.execute(
                """
                INSERT INTO `shares` 
                (time, rem_host, worker, our_result, upstream_result, 
                  reason, solution, block_num, prev_block_hash, 
                  useragent, difficulty) 
                VALUES
                (FROM_UNIXTIME(%(time)s), %(host)s, 
                  (SELECT `id` FROM `pool_worker` WHERE `username` = %(uname)s),
                  %(lres)s, 0, %(reason)s, %(solution)s, 
                  %(blocknum)s, %(hash)s, '', %(difficulty)s)
                """,
                {
                    "time": v[4],
                    "host": v[6],
                    "uname": v[0],
                    "lres": v[5],
                    "reason": v[9],
                    "solution": v[2],
                    "blocknum": v[7],
                    "hash": v[8],
                    "difficulty": v[3]
                }
            )

        self.execute(
            """
            SELECT `parameter`, `value` 
            FROM `pool` 
            WHERE `parameter` = 'round_best_share'
              OR `parameter` = 'round_shares'
              OR `parameter` = 'bitcoin_difficulty'
              OR `parameter` = 'round_progress'
            """
        )
            
        current_parameters = {}
        
        for data in self.dbc.fetchall():
            current_parameters[data[0]] = data[1]
        
        round_best_share = int(current_parameters['round_best_share'])
        difficulty = float(current_parameters['bitcoin_difficulty'])
        round_shares = int(current_parameters['round_shares']) + total_shares
            
        updates = [
            {
                "param": "round_shares",
                "value": round_shares
            },
            {
                "param": "round_progress",
                "value": 0 if difficulty == 0 else (round_shares / difficulty) * 100
            }
        ]
            
        if best_diff > round_best_share:
            updates.append({
                "param": "round_best_share",
                "value": best_diff
            })
        
        self.executemany(
            """
            UPDATE `pool` 
            SET `value` = %(value)s
            WHERE `parameter` = %(param)s
            """,
            updates
        )
    
        for k, v in checkin_times.items():
            self.execute(
                """
                UPDATE `pool_worker`
                SET `last_checkin` = FROM_UNIXTIME(%(time)s), 
                  `total_shares` = `total_shares` + %(shares)s,
                  `total_rejects` = `total_rejects` + %(rejects)s
                WHERE `username` = %(uname)s
                """,
                {
                    "time": v["time"],
                    "shares": v["shares"],
                    "rejects": v["rejects"], 
                    "uname": k
                }
            )
        
        self.dbh.commit()


    def found_block(self, data):
        # for database compatibility we are converting our_worker to Y/N format
        #if data[5]:
        #    data[5] = 'Y'
        #else:
        #    data[5] = 'N'
        # Note: difficulty = -1 here
        self.execute(
            """
            UPDATE `shares`
            SET `upstream_result` = %(result)s,
              `solution` = %(solution)s
            WHERE `time` = FROM_UNIXTIME(%(time)s)
              AND `worker` =  (SELECT id 
                FROM `pool_worker` 
                WHERE `username` = %(uname)s)
            LIMIT 1
            """,
            {
                "result": data[5], 
                "solution": data[2], 
                "time": data[4], 
                "uname": data[0]
            }
        )
        
        if data[5] == True:
            self.execute(
                """
                UPDATE `pool_worker`
                SET `total_found` = `total_found` + 1
                WHERE `username` = %(uname)s
                """,
                {
                    "uname": data[0]
                }
            )
            self.execute(
                """
                SELECT `value`
                FROM `pool`
                WHERE `parameter` = 'pool_total_found'
                """
            )
            total_found = int(self.dbc.fetchone()[0]) + 1
            
            self.executemany(
                """
                UPDATE `pool`
                SET `value` = %(value)s
                WHERE `parameter` = %(param)s
                """,
                [
                    {
                        "param": "round_shares",
                        "value": "0"
                    },
                    {
                        "param": "round_progress",
                        "value": "0"
                    },
                    {
                        "param": "round_best_share",
                        "value": "0"
                    },
                    {
                        "param": "round_start",
                        "value": time.time()
                    },
                    {
                        "param": "pool_total_found",
                        "value": total_found
                    }
                ]
            )
            
        self.dbh.commit()
        
    def update_pool_info(self, pi):
        self.executemany(
            """
            UPDATE `pool`
            SET `value` = %(value)s
            WHERE `parameter` = %(param)s
            """,
            [
                {
                    "param": "bitcoin_blocks",
                    "value": pi['blocks']
                },
                {
                    "param": "bitcoin_balance",
                    "value": pi['balance']
                },
                {
                    "param": "bitcoin_connections",
                    "value": pi['connections']
                },
                {
                    "param": "bitcoin_difficulty",
                    "value": pi['difficulty']
                },
                {
                    "param": "bitcoin_infotime",
                    "value": time.time()
                }
            ]
        )
        
        self.dbh.commit()

    def get_pool_stats(self):
        self.execute(
            """
            SELECT * FROM `pool`
            """
        )
        
        ret = {}
        
        for data in self.dbc.fetchall():
            ret[data[0]] = data[1]
            
        return ret

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
                "difficulty": int(data[7])
            }
            
        return ret
