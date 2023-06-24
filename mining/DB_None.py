import stratum.logger
log = stratum.logger.get_logger('None')

class DB_None():
    def __init__(self):
	return

    def updateStats(self,averageOverTime):
	return

    def import_shares(self,data):
	return

    def found_block(self,data):
	return

    def get_user(self, id_or_username):
	return

    def list_users(self):
	return

    def delete_user(self,username):
	return

    def insert_user(self,username,password):
	return

    def update_user(self,username,password):
	return

    def check_password(self,username,password):
	return True

    def update_pool_info(self,pi):
	return

    def clear_worker_diff(self):
	return

    def get_pool_stats(self):
        return {}

    def get_workers_stats(self):
	return {}

    def check_tables(self):
	return True

    def close(self):
	return

    def update_worker_diff(self, username, diff):
        return
