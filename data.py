class data:
	def __init__(self):
		"Class containing all the data"

		self.init_data()

	def init_data(self):
		"""Initilize the data

		The structure of self.input_info is as follows:  The fields of the first dimension correspond
		to each relaxation data set and is flexible in size, ie len(self.input_info) = number of data sets.
		The second dimension have the following fixed fields taken from the file 'input':
			0 - Data label (NOE, R1, or R2)
			1 - NMR frequency label
			2 - NMR proton frequency in MHz
			3 - The name of the file containing the relaxation data
		
		The structure of self.relax_data is as follows:  The first dimension corresponds to each
		relaxation data set as in self.input_info.  The fields point to 2D data structures containing
		the data from the relaxation file (missing the single header line).
		"""

		self.stage = 0
		self.num_frq = 0
		self.input_info = []
		self.relax_data = []
		self.num_data_sets = 0
		self.models = ["m1", "m2", "m3", "m4", "m5"]
		self.ftests_short = ["f-m1m2", "f-m1m3"]
		self.ftests_full = ["f-m1m2", "f-m1m3", "f-m2m4", "f-m2m5", "f-m3m4"]
	
