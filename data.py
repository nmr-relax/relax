class data:
	def __init__(self):
		"Class containing all the data"

		self.init_data()
		self.aic = self.init_aic()
		self.bic = self.init_bic()
		self.palmer = self.init_palmer()


	class init_aic:
		def __init__(self):
			"Data specific for the modelfree analysis using AIC model selection."

			self.name = 'AIC'
			self.stage = '0'


	class init_bic:
		def __init__(self):
			"Data specific for the modelfree analysis using BIC model selection."

			self.name = 'BIC'
			self.stage = '0'


	class init_palmer:
		def __init__(self):
			"Data specific for Palmer's modelfree analysis."

			self.name = 'Palmer'
			self.stage = '0'


	def init_data(self):
		"""Initilize the data

		The structure of self.nmr_frq is as follows:  The length of the first dimension is equal to the number
		of field strengths.  The fields of the second are:
			0 - NMR frequency label
			1 - NMR proton frequency in MHz

		The structure of self.input_info is as follows:  The fields of the first dimension correspond
		to each relaxation data set and is flexible in size, ie len(self.input_info) = number of data sets.
		The second dimension have the following fixed fields taken from the file 'input':
			0 - Data label (NOE, R1, or R2)
			1 - NMR frequency label
			2 - NMR proton frequency in MHz
			3 - The name of the file containing the relaxation data
		
		The structure of self.relax_data is as follows:  The first dimension corresponds to each
		relaxation data set as in self.input_info.  The fields point to 2D data structures containing
		the data from the relaxation file (missing the single header line), ie:
			[res][0] - Residue number
			[res][1] - Residue name
			[res][2] - Relaxation value
			[res][3] - Relaxation error
		"""

		self.nmr_frq = []
		self.input_info = []
		self.relax_data = []
		self.num_data_sets = 0
		self.runs = []

		self.data = {}
