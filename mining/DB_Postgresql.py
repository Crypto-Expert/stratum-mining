import time
import hashlib
from stratum import settings
import stratum.logger
log = stratum.logger.get_logger('DB_Postgresql')

import psycopg2
from psycopg2 import extras
                
class DB_Postgresql():
    def __init__(self):
        log.debug("Connecting to DB")
        self.dbh = psycopg2.connect("host='"+settings.DB_PGSQL_HOST+"' dbname='"+settings.DB_PGSQL_DBNAME+"' user='"+settings.DB_PGSQL_USER+\
                "' password='"+settings.DB_PGSQL_PASS+"'")
        # TODO -- set the schema
        self.dbc = self.dbh.cursor()
        
        if hasattr(settings, 'PASSWORD_SALT'):
            self.salt = settings.PASSWORD_SALT
        else:
            raise ValueError("PASSWORD_SALT isn't set, please set in config.py")

    def updateStats(self,averageOverTime):
        log.debug("Updating Stats")
        # Note: we are using transactions... so we can set the speed = 0 and it doesn't take affect until we are commited.
        self.dbc.execute("update pool_worker set speed = 0, alive = 'f'");
        stime = '%.2f' % ( time.time() - averageOverTime );
        self.dbc.execute("select username,SUM(difficulty) from shares where time > to_timestamp(%s) group by username", [stime])
        total_speed = 0
        for name,shares in self.dbc.fetchall():
            speed = int(int(shares) * pow(2,32)) / ( int(averageOverTime) * 1000 * 1000)
            total_speed += speed
            self.dbc.execute("update pool_worker set speed = %s, alive = 't' where username = %s", (speed,name))
        self.dbc.execute("update pool set value = %s where parameter = 'pool_speed'",[total_speed])
        self.dbh.commit()
    
    def archive_check(self):
        # Check for found shares to archive
        self.dbc.execute("select time from shares where upstream_result = true order by time limit 1")
        data = self.dbc.fetchone()
        if data is None or (data[0] + settings.ARCHIVE_DELAY) > time.time() :
            return False
        return data[0]

    def archive_found(self,found_time):
        self.dbc.execute("insert into shares_archive_found select * from shares where upstream_result = true and time <= to_timestamp(%s)", [found_time])
        self.dbh.commit()

    def archive_to_db(self,found_time):
        self.dbc.execute("insert into shares_archive select * from shares where time <= to_timestamp(%s)",[found_time])        
        self.dbh.commit()

    def archive_cleanup(self,found_time):
        self.dbc.execute("delete from shares where time <= to_timestamp(%s)",[found_time])
        self.dbh.commit()

    def archive_get_shares(self,found_time):
        self.dbc.execute("select * from shares where time <= to_timestamp(%s)",[found_time])
        return self.dbc

    def import_shares(self,data):
        log.debug("Importing Shares")
#               0           1            2          3          4         5        6  7            8         9              10
#        data: [worker_name,block_header,block_hash,difficulty,timestamp,is_valid,ip,block_height,prev_hash,invalid_reason,best_diff]
        checkin_times = {}
        total_shares = 0
        best_diff = 0
        for k,v in enumerate(data):
            if settings.DATABASE_EXTEND :
                total_shares += v[3]
                if v[0] in checkin_times:
                    if v[4] > checkin_times[v[0]] :
                        checkin_times[v[0]]["time"] = v[4]
                else:
                    checkin_times[v[0]] = {"time": v[4], "shares": 0, "rejects": 0 }

                if v[5] == True :
                    checkin_times[v[0]]["shares"] += v[3]
                else :
                    checkin_times[v[0]]["rejects"] += v[3]

                if v[10] > best_diff:
                    best_diff = v[10]

                self.dbc.execute("insert into shares " +\
                        "(time,rem_host,username,our_result,upstream_result,reason,solution,block_num,prev_block_hash,useragent,difficulty) " +\
                        "VALUES (to_timestamp(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (v[4],v[6],v[0],bool(v[5]),False,v[9],'',v[7],v[8],'',v[3]) )
            else :
                self.dbc.execute("insert into shares (time,rem_host,username,our_result,upstream_result,reason,solution) VALUES " +\
                        "(to_timestamp(%s),%s,%s,%s,%s,%s,%s)",
                        (v[4],v[6],v[0],bool(v[5]),False,v[9],'') )

        if settings.DATABASE_EXTEND :
            self.dbc.execute("select value from pool where parameter = 'round_shares'")
            round_shares = int(self.dbc.fetchone()[0]) + total_shares
            self.dbc.execute("update pool set value = %s where parameter = 'round_shares'",[round_shares])

            self.dbc.execute("select value from pool where parameter = 'round_best_share'")
            round_best_share = int(self.dbc.fetchone()[0])
            if best_diff > round_best_share:
                self.dbc.execute("update pool set value = %s where parameter = 'round_best_share'",[best_diff])

            self.dbc.execute("select value from pool where parameter = 'bitcoin_difficulty'")
            difficulty = float(self.dbc.fetchone()[0])

            if difficulty == 0:
                progress = 0
            else:
                    progress = (round_shares/difficulty)*100
            self.dbc.execute("update pool set value = %s where parameter = 'round_progress'",[progress])
        
            for k,v in checkin_times.items():
                self.dbc.execute("update pool_worker set last_checkin = to_timestamp(%s), total_shares = total_shares + %s, total_rejects = total_rejects + %s where username = %s",
                        (v["time"],v["shares"],v["rejects"],k))

        self.dbh.commit()


    def found_block(self,data):
        # Note: difficulty = -1 here
        self.dbc.execute("update shares set upstream_result = %s, solution = %s where id in (select id from shares where time = to_timestamp(%s) and username = %s limit 1)",
                (bool(data[5]),data[2],data[4],data[0]))
        if settings.DATABASE_EXTEND and data[5] == True :
            self.dbc.execute("update pool_worker set total_found = total_found + 1 where username = %s",(data[0],))
            self.dbc.execute("select value from pool where parameter = 'pool_total_found'")
            total_found = int(self.dbc.fetchone()[0]) + 1
            self.dbc.executemany("update pool set value = %s where parameter = %s",[(0,'round_shares'),
                (0,'round_progress'),
                (0,'round_best_share'),
                (time.time(),'round_start'),
                (total_found,'pool_total_found')
                ])
        self.dbh.commit()
                
    def get_user(self, id_or_username):
        log.debug("Finding user with id or username of %s", id_or_username)
        cursor = self.dbh.cursor(cursor_factory=extras.DictCursor)
        
        cursor.execute(
            """
            SELECT *
            FROM pool_worker
            WHERE id = %(id)s
              OR username = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username
            }
        )
        
        user = cursor.fetchone()
        cursor.close()
        return user
        
    def list_users(self):
        cursor = self.dbh.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(
            """
            SELECT *
            FROM pool_worker
            WHERE id > 0
            """
        )
        
        while True:
            results = cursor.fetchmany()
            if not results:
                break
            
            for result in results:
                yield result

    def delete_user(self, id_or_username):
        log.debug("Deleting Username")
        self.dbc.execute(
            """
            delete from pool_worker where id = %(id)s or username = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username
            }
        )
        self.dbh.commit()

    def insert_user(self,username,password):
        log.debug("Adding Username/Password")
        m = hashlib.sha1()
        m.update(password)
        m.update(self.salt)
        self.dbc.execute("insert into pool_worker (username,password) VALUES (%s,%s)",
                (username, m.hexdigest() ))
        self.dbh.commit()
        
        return str(username)

    def update_user(self, id_or_username, password):
        log.debug("Updating Username/Password")
        m = hashlib.sha1()
        m.update(password)
        m.update(self.salt)
        self.dbc.execute(
            """
            update pool_worker set password = %(pass)s where id = %(id)s or username = %(uname)s
            """,
            {
                "id": id_or_username if id_or_username.isdigit() else -1,
                "uname": id_or_username,
                "pass": m.hexdigest()
            }
        )
        self.dbh.commit()

    def update_worker_diff(self,username,diff):
        self.dbc.execute("update pool_worker set difficulty = %s where username = %s",(diff,username))
        self.dbh.commit()
    
    def clear_worker_diff(self):
        if settings.DATABASE_EXTEND == True :
            self.dbc.execute("update pool_worker set difficulty = 0")
            self.dbh.commit()

    def check_password(self,username,password):
        log.debug("Checking Username/Password")
        m = hashlib.sha1()
        m.update(password)
        m.update(self.salt)
        self.dbc.execute("select COUNT(*) from pool_worker where username = %s and password = %s",
                (username, m.hexdigest() ))
        data = self.dbc.fetchone()
        if data[0] > 0 :
            return True
        return False

    def update_pool_info(self,pi):
        self.dbc.executemany("update pool set value = %s where parameter = %s",[(pi['blocks'],"bitcoin_blocks"),
                (pi['balance'],"bitcoin_balance"),
                (pi['connections'],"bitcoin_connections"),
                (pi['difficulty'],"bitcoin_difficulty"),
                (time.time(),"bitcoin_infotime")
                ])
        self.dbh.commit()

    def get_pool_stats(self):
        self.dbc.execute("select * from pool")
        ret = {}
        for data in self.dbc.fetchall():
            ret[data[0]] = data[1]
        return ret

    def get_workers_stats(self):
        self.dbc.execute("select username,speed,last_checkin,total_shares,total_rejects,total_found,alive,difficulty from pool_worker")
        ret = {}
        for data in self.dbc.fetchall():
            ret[data[0]] = { "username" : data[0],
                "speed" : data[1],
                "last_checkin" : time.mktime(data[2].timetuple()),
                "total_shares" : data[3],
                "total_rejects" : data[4],
                "total_found" : data[5],
                "alive" : data[6],
                "difficulty" : data[7] }
        return ret

    def close(self):
        self.dbh.close()

    def check_tables(self):
        log.debug("Checking Tables")

        shares_exist = False
        self.dbc.execute("select COUNT(*) from pg_catalog.pg_tables where schemaname = %(schema)s and tablename = 'shares'",
                {"schema": settings.DB_PGSQL_SCHEMA })
        data = self.dbc.fetchone()
        if data[0] <= 0 :
            self.update_version_1()
        
        if settings.DATABASE_EXTEND == True :
            self.update_tables()

        
    def update_tables(self):
        version = 0
        current_version = 7
        while version < current_version :
            self.dbc.execute("select value from pool where parameter = 'DB Version'")
            data = self.dbc.fetchone()
            version = int(data[0])
            if version < current_version :
                log.info("Updating Database from %i to %i" % (version, version +1))
                getattr(self, 'update_version_' + str(version) )()
                    
    def update_version_1(self):
        if settings.DATABASE_EXTEND == True :
            self.dbc.execute("create table shares" +\
                "(id serial primary key,time timestamp,rem_host TEXT, username TEXT, our_result BOOLEAN, upstream_result BOOLEAN, reason TEXT, solution TEXT, " +\
                "block_num INTEGER, prev_block_hash TEXT, useragent TEXT, difficulty INTEGER)")
            self.dbc.execute("create index shares_username ON shares(username)")
            self.dbc.execute("create table pool_worker" +\
                        "(id serial primary key,username TEXT, password TEXT, speed INTEGER, last_checkin timestamp)")
            self.dbc.execute("create index pool_worker_username ON pool_worker(username)")
            self.dbc.execute("alter table pool_worker add total_shares INTEGER default 0")
            self.dbc.execute("alter table pool_worker add total_rejects INTEGER default 0")
            self.dbc.execute("alter table pool_worker add total_found INTEGER default 0")
            self.dbc.execute("create table pool(parameter TEXT, value TEXT)")
            self.dbc.execute("insert into pool (parameter,value) VALUES ('DB Version',2)")
        else :
            self.dbc.execute("create table shares" + \
                "(id serial,time timestamp,rem_host TEXT, username TEXT, our_result BOOLEAN, upstream_result BOOLEAN, reason TEXT, solution TEXT)")
            self.dbc.execute("create index shares_username ON shares(username)")
            self.dbc.execute("create table pool_worker(id serial,username TEXT, password TEXT)")
            self.dbc.execute("create index pool_worker_username ON pool_worker(username)")
        self.dbh.commit()

    def update_version_2(self):
        log.info("running update 2")
        self.dbc.executemany("insert into pool (parameter,value) VALUES (%s,%s)",[('bitcoin_blocks',0),
                ('bitcoin_balance',0),
                ('bitcoin_connections',0),
                ('bitcoin_difficulty',0),
                ('pool_speed',0),
                ('pool_total_found',0),
                ('round_shares',0),
                ('round_progress',0),
                ('round_start',time.time())
                ])
        self.dbc.execute("update pool set value = 3 where parameter = 'DB Version'")
        self.dbh.commit()
        
    def update_version_3(self):
        log.info("running update 3")
        self.dbc.executemany("insert into pool (parameter,value) VALUES (%s,%s)",[
                ('round_best_share',0),
                ('bitcoin_infotime',0)
                ])
        self.dbc.execute("alter table pool_worker add alive BOOLEAN")
        self.dbc.execute("update pool set value = 4 where parameter = 'DB Version'")
        self.dbh.commit()
        
    def update_version_4(self):
        log.info("running update 4")
        self.dbc.execute("alter table pool_worker add difficulty INTEGER default 0")
        self.dbc.execute("create table shares_archive" +\
                "(id serial primary key,time timestamp,rem_host TEXT, username TEXT, our_result BOOLEAN, upstream_result BOOLEAN, reason TEXT, solution TEXT, " +\
                "block_num INTEGER, prev_block_hash TEXT, useragent TEXT, difficulty INTEGER)")
        self.dbc.execute("create table shares_archive_found" +\
                "(id serial primary key,time timestamp,rem_host TEXT, username TEXT, our_result BOOLEAN, upstream_result BOOLEAN, reason TEXT, solution TEXT, " +\
                "block_num INTEGER, prev_block_hash TEXT, useragent TEXT, difficulty INTEGER)")
        self.dbc.execute("update pool set value = 5 where parameter = 'DB Version'")
        self.dbh.commit()
        
    def update_version_5(self):
        log.info("running update 5")
        # Adding Primary key to table: pool
        self.dbc.execute("alter table pool add primary key (parameter)")
        self.dbh.commit()
        # Adjusting indicies on table: shares
        self.dbc.execute("DROP INDEX shares_username")
        self.dbc.execute("CREATE INDEX shares_time_username ON shares(time,username)")
        self.dbc.execute("CREATE INDEX shares_upstreamresult ON shares(upstream_result)")
        self.dbh.commit()
        
        self.dbc.execute("update pool set value = 6 where parameter = 'DB Version'")
        self.dbh.commit()
        
    def update_version_6(self):
        log.info("running update 6")
        
        try:
            self.dbc.execute("CREATE EXTENSION pgcrypto")
        except psycopg2.ProgrammingError:
            log.info("pgcrypto already added to database")
        except psycopg2.OperationalError:
            raise Exception("Could not add pgcrypto extension to database. Have you got it installed? Ubuntu is postgresql-contrib")
        self.dbh.commit()
        
        # Optimising table layout
        self.dbc.execute("ALTER TABLE pool " +\
            "ALTER COLUMN parameter TYPE character varying(128), ALTER COLUMN value TYPE character varying(512);")
        self.dbh.commit()
        
        self.dbc.execute("UPDATE pool_worker SET password = encode(digest(concat(password, %s), 'sha1'), 'hex') WHERE id > 0", [self.salt])
        self.dbh.commit()
        
        self.dbc.execute("ALTER TABLE pool_worker " +\
            "ALTER COLUMN username TYPE character varying(512), ALTER COLUMN password TYPE character(40), " +\
            "ADD CONSTRAINT username UNIQUE (username)")
        self.dbh.commit()
        
        self.dbc.execute("update pool set value = 7 where parameter = 'DB Version'")
        self.dbh.commit()

