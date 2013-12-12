import stratum.logger
log = stratum.logger.get_logger('None')
                
class DB_None():
    def __init__(self):
	log.debug("Connecting to DB")

    def updateStats(self,averageOverTime):
	log.debug("Updating Stats")

    def import_shares(self,data):
	log.debug("Importing Shares")

    def found_block(self,data):
	log.debug("Found Block")
    
    def get_user(self, id_or_username):
        log.debug("Get User")

    def list_users(self):
        log.debug("List Users")

    def delete_user(self,username):
	log.debug("Deleting Username")

    def insert_user(self,username,password):
	log.debug("Adding Username/Password")

    def update_user(self,username,password):
	log.debug("Updating Username/Password")

    def check_password(self,username,password):
	log.debug("Checking Username/Password")
	return True
    
    def update_pool_info(self,pi):
	log.debug("Update Pool Info")

    def get_pool_stats(self):
	log.debug("Get Pool Stats")
	ret = {}
	return ret

    def get_workers_stats(self):
	log.debug("Get Workers Stats")
	ret = {}
	return ret

    def check_tables(self):
	log.debug("Checking Tables")

    def close(self):
	log.debug("Close Connection")
	
