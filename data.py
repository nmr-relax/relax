from math import pi


class data:
	def __init__(self, mf):
		"Class containing all the data"

		self.mf = mf

		self.init_data()
		self.init_constants()
		self.mfin = self.mfin_data(self.mf)
		self.asymptotic = self.init_asymptotic()
		self.bootstrap = self.init_bootstrap()
		self.farrow = self.init_farrow()
		self.palmer = self.init_palmer()
		self.true = self.init_true()



	class init_asymptotic:
		def __init__(self):
			"Data specific for the model-free analysis using asymptotic model selection."

			self.name = 'Asymptotic'



	class init_bootstrap:
		def __init__(self):
			"Data specific for the model-free analysis using bootstrap model selection."

			self.name = 'Bootstrap'



	class init_farrow:
		def __init__(self):
			"Data specific for Farrow's model-free analysis."

			self.name = 'Farrow'



	class init_palmer:
		def __init__(self):
			"Data specific for Palmer's model-free analysis."

			self.name = 'Palmer'



	class init_true:
		def __init__(self):
			"Data specific for modelfree analysis using the overall discrepency."

			self.name = 'True'
			self.op_data = []


	class mfin_data:
		def __init__(self, mf):
			"Variables for the file mfin"

			self.mf = mf


		def default_data(self):

			self.diff = self.mf.data.usr_param.diff
			self.diff_search = 'none'
			self.algorithm = 'fix'
			self.sims = 'n'
			self.sim_type = 'pred'
			self.trim = self.mf.data.usr_param.trim
			self.selection = 'none'
			self.num_sim = self.mf.data.usr_param.num_sim
			self.num_fields = `len(self.mf.data.nmr_frq)`



	def calc_constants(self):
		"Calculate the dipolar and CSA constants."

		self.rnh = float(self.mf.data.usr_param.const['rxh']) * 1e-10
		self.csa = float(self.mf.data.usr_param.const['csa']) * 1e-6

		# Dipolar constant.

		dip = (4*pi/self.mu0) * (self.h_bar*self.gn*self.gh) / (2 * self.rnh**3)
		self.dipole_const = dip**2
		print self.dipole_const

		self.csa_const = []
		for i in range(len(self.nmr_frq)):
			csa_const = ( self.frq[i][1] * self.csa ) ** 2 / 3
			self.csa_const.append(csa_const)
		print self.csa_const



	def calc_frq(self):
		"Calculate all the frequencies which lead to relaxation."

		self.frq = []
		for i in range(len(self.nmr_frq)):
			self.frq.append([])
			frqN = 2*pi * ( float(self.nmr_frq[i][1]) * 1e6 ) * ( self.gh / self.gn )
			frqH = 2*pi * ( float(self.nmr_frq[i][1]) * 1e6 )
			self.frq[i].append(0)
			self.frq[i].append(frqN)
			self.frq[i].append(frqH + frqN)
			self.frq[i].append(frqH)
			self.frq[i].append(frqH - frqN)


	def init_constants(self):
		self.gn = -2.71e-7
		self.gh = 0.27e-7
		self.h = 6.626e32
		self.h_bar = self.h / ( 2*pi )
		self.mu0 = 4*pi*1e7


	def init_data(self):
		"""Initilize the data

		The structure of self.nmr_frq is as follows:  The length of the first dimension is equal to the number
		of field strengths.  The fields of the second are:
			0 - NMR frequency label
			1 - NMR proton frequency in MHz
			2 - R1 flag (0 or 1 depending if data is present).
			3 - R2 flag (0 or 1 depending if data is present).
			4 - NOE flag (0 or 1 depending if data is present).

		The structure of self.input_info is as follows:  The fields of the first dimension correspond
		to each relaxation data set and is flexible in size, ie len(self.input_info) = number of data sets.
		The second dimension have the following fixed fields taken from the file 'input':
			0 - Data type (NOE, R1, or R2)
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

		self.stage = '0'

		self.data = {}
		self.results = []
