import time
import hashlib
import lib.settings as settings
import lib.logger
log = lib.logger.get_logger('DB_Mysql')

import MySQLdb
                
class DB_Mysql():
    def __init__(self):
        log.debug("Connecting to DB")
        
        required_settings = ['PASSWORD_SALT', 'DB_MYSQL_HOST', 
                             'DB_MYSQL_USER', 'DB_MYSQL_PASS', 
                             'DB_MYSQL_DBNAME','DB_MYSQL_PORT']
        
        for setting_name in required_settings:
            if not hasattr(settings, setting_name):
                raise ValueError("%s isn't set, please set in config.py" % setting_name)
        
        self.salt = getattr(settings, 'PASSWORD_SALT')
        self.connect()
        
    def connect(self):
        self.dbh = MySQLdb.connect(
            getattr(settings, 'DB_MYSQL_HOST'), 
            getattr(settings, 'DB_MYSQL_USER'),
            getattr(settings, 'DB_MYSQL_PASS'), 
            getattr(settings, 'DB_MYSQL_DBNAME'),
            getattr(settings, 'DB_MYSQL_PORT')
        )
        self.dbc = self.dbh.cursor()
        self.dbh.autocommit(True)
            
    def execute(self, query, args=None):
        try:
            self.dbc.execute(query, args)
        except MySQLdb.OperationalError:
            log.debug("MySQL connection lost during execute, attempting reconnect")
            self.connect()
            self.dbc = self.dbh.cursor()
            
            self.dbc.execute(query, args)
            
    def executemany(self, query, args=None):
        try:
            self.dbc.executemany(query, args)
        except MySQLdb.OperationalError:
            log.debug("MySQL connection lost during executemany, attempting reconnect")
            self.connect()
            self.dbc = self.dbh.cursor()
            
            self.dbc.executemany(query, args)
    
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
                    "time": data[4],
                    "host": data[6],
                    "uname": data[0],
                    "lres": data[5],
                    "result": data[5],
                    "reason": data[9],
                    "solution": data[2]
                }
            )

            self.dbh.commit()

        
    def list_users(self):
        self.execute(
            """
            SELECT *
            FROM `pool_worker`
            WHERE `id`> 0
            """
        )
        
        while True:
            results = self.dbc.fetchmany()
            if not results:
                break
            
            for result in results:
                yield result
                
                
    def get_user(self, id_or_username):
        log.debug("Finding user with id or username of %s", id_or_username)
        
        self.execute(
            """
            SELECT *
            FROM `pool_worker`
            WHERE `id` = %(id)s
              OR `username` = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username
            }
        )
        
        user = self.dbc.fetchone()
        return user

    def get_uid(self, id_or_username):
        log.debug("Finding user id of %s", id_or_username)
        uname = id_or_username.split(".", 1)[0]
        self.execute("SELECT `id` FROM `accounts` where username = %s", (uname))
        row = self.dbc.fetchone()

        if row is None:
            return False
        else:
            uid = row[0]
            return uid

    def insert_worker(self, account_id, username, password):
        log.debug("Adding new worker %s", username)
        query = "INSERT INTO pool_worker"
        self.execute(query + '(account_id, username, password) VALUES (%s, %s, %s);', (account_id, username, password))
        self.dbh.commit()
        return str(username)
        

    def delete_user(self, id_or_username):
        if id_or_username.isdigit() and id_or_username == '0':
            raise Exception('You cannot delete that user')
        
        log.debug("Deleting user with id or username of %s", id_or_username)
        
        self.execute(
            """
            UPDATE `shares`
            SET `username` = 0
            WHERE `username` = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username
            }
        )
        
        self.execute(
            """
            DELETE FROM `pool_worker`
            WHERE `id` = %(id)s
              OR `username` = %(uname)s
            """, 
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username
            }
        )
        
        self.dbh.commit()

    def insert_user(self, username, password):
        log.debug("Adding new user %s", username)
        
        self.execute(
            """
            INSERT INTO `pool_worker`
            (`username`, `password`)
            VALUES
            (%(uname)s, %(pass)s)
            """,
            {
                "uname": username, 
                "pass": password
            }
        )
        
        self.dbh.commit()
        
        return str(username)

    def update_user(self, id_or_username, password):
        log.debug("Updating password for user %s", id_or_username);
        
        self.execute(
            """
            UPDATE `pool_worker`
            SET `password` = %(pass)s
            WHERE `id` = %(id)s
              OR `username` = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username,
                "pass": password
            }
        )
        
        self.dbh.commit()

    def check_password(self, username, password):
        log.debug("Checking username/password for %s", username)
        
        self.execute(
            """
            SELECT COUNT(*) 
            FROM `pool_worker`
            WHERE `username` = %(uname)s
              AND `password` = %(pass)s
            """,
            {
                "uname": username, 
                "pass": password
            }
        )
        
        data = self.dbc.fetchone()
        if data[0] > 0:
            return True
        
        return False

    def get_workers_stats(self):
        self.execute(
            """
            SELECT `username`, `speed`, `last_checkin`, `total_shares`,
              `total_rejects`, `total_found`, `alive`
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
            }
            
        return ret
    def get_uid(self, id_or_username):
        log.debug("Finding user id of %s", id_or_username)
        uname = id_or_username.split(".", 1)[0]
        self.execute("SELECT `id` FROM `accounts` where username = %s", (uname))
        row = self.dbc.fetchone()
        
       
        if row is None:
            return False
        else:
            uid = row[0]
            return uid
    
    
    def insert_worker(self, account_id, username, password):
        log.debug("Adding new worker %s", username)
        query = "INSERT INTO pool_worker"
        self.execute(query + '(account_id, username, password) VALUES (%s, %s, %s);', (account_id, username, password))
        self.dbh.commit()
        return str(username)
        


    def close(self):
        self.dbh.close()

    def check_tables(self):
        log.debug("Checking Database")
        
        self.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE `table_schema` = %(schema)s
              AND `table_name` = 'shares'
            """,
            {
                "schema": getattr(settings, 'DB_MYSQL_DBNAME')
            }
        )
        
        data = self.dbc.fetchone()
        
        if data[0] <= 0:
           raise Exception("There is no shares table. Have you imported the schema?")
 

