class data:
	def __init__(self):
		"Class containing all the data"

		self.init_data()

	def init_data(self):
		"Initilize the data"

		self.stage = 0
		self.num_frq = 0
		self.input_info = []
		self.num_data_sets = 0
		self.relax_data = []
		self.models = ["m1", "m2", "m3", "m4", "m5"]
		self.ftests_short = ["f-m1m2", "f-m1m3"]
		self.ftests_full = ["f-m1m2", "f-m1m3", "f-m2m4", "f-m2m5", "f-m3m4"]
