class Sha256_Coin:
		# Algorithm Needed
		def algo(self): 
			self.algorithm = ALGO[2]
			return self.algorithm
		# Difficulty 1
		def diff1(self):
			self.DIFF1 = DIFF[3]
			return self.DIFF1
		# Header modifications
		def header(self):
			self.header = False
			return self.header
