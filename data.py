from math import pi


class data:
	def __init__(self, mf):
		"Class containing all the program data"

		self.mf = mf

		self.init_data()
		self.init_constants()
		self.mfin = self.mfin_data(self.mf)
		self.asymptotic = self.init_asymptotic()
		self.bootstrap = self.init_bootstrap()
		self.cv = self.init_cv()
		self.farrow = self.init_farrow()
		self.palmer = self.init_palmer()
		self.overall_disc = self.init_overall_disc()



	class init_asymptotic:
		def __init__(self):
			"Data specific for the model-free analysis using asymptotic model selection."

			self.name = 'Asymptotic'



	class init_bootstrap:
		def __init__(self):
			"Data specific for the model-free analysis using bootstrap model selection."

			self.name = 'Bootstrap'



	class init_cv:
		def __init__(self):
			"Data specific for the model-free analysis using bootstrap model selection."

			self.name = 'Cross validation'
			self.cv_crit = []



	class init_farrow:
		def __init__(self):
			"Data specific for Farrow's model-free analysis."

			self.name = 'Farrow'



	class init_palmer:
		def __init__(self):
			"Data specific for Palmer's model-free analysis."

			self.name = 'Palmer'



	class init_overall_disc:
		def __init__(self):
			"Data specific for model-free analysis using the overall discrepancy."

			self.name = 'Overall'
			self.op_data = []


	class mfin_data:
		def __init__(self, mf):
			"Variables for the file mfin"

			self.mf = mf


		def default_data(self):

			self.diff = self.mf.usr_param.diff
			self.diff_search = 'none'
			self.algorithm = 'fix'
			self.sims = 'n'
			self.sim_type = 'pred'
			self.trim = self.mf.usr_param.trim
			self.selection = 'none'
			self.num_sim = self.mf.usr_param.num_sim
			self.num_fields = `len(self.mf.usr_param.nmr_frq)`



	def calc_constants(self):
		"Calculate the dipolar and CSA constants."

		self.rnh = float(self.mf.usr_param.const['rxh']) * 1e-10
		self.csa = float(self.mf.usr_param.const['csa']) * 1e-6

		# Dipolar constant.

		dip = (self.mu0/(4.0*pi)) * self.h_bar * self.gh * self.gx * self.rnh**-3
		self.dipole_const = (dip**2) / 4.0
		dip_temp = self.dipole_const / 1e9

		self.csa_const = []
		csa_temp = []
		for i in range(len(self.mf.usr_param.nmr_frq)):
			csa_const = (self.csa**2) * (self.frq[i][1]**2) / 3.0
			self.csa_const.append(csa_const)
			csa_temp.append(csa_const/1e9)

		# Print section.
		#print "r(NH): " + `self.rnh`
		#print "CSA: " + `self.csa`
		#print "CSA^2: " + `self.csa**2`
		#print "gH: " + `self.gh`
		#print "gN: " + `self.gx`
		#print "h-bar: " + `self.h_bar`
		#print "mu0: " + `self.mu0`
		#print "frq1: " + `self.frq[0][1]`
		#print "frq2: " + `self.frq[1][1]`
		#print dip_temp
		#print csa_temp



	def calc_frq(self):
		"Calculate all the frequencies which lead to relaxation."

		self.frq = []
		for i in range(len(self.mf.usr_param.nmr_frq)):
			self.frq.append([])
			frqH = 2.0*pi * ( float(self.mf.usr_param.nmr_frq[i][1]) * 1e6 )
			frqN = frqH * ( self.gx / self.gh )
			self.frq[i].append(0.0)
			self.frq[i].append(frqN)
			self.frq[i].append(frqH - frqN)
			self.frq[i].append(frqH)
			self.frq[i].append(frqH + frqN)


	def init_constants(self):
		self.gh = 26.7522e7
		self.gx = -2.7126e7
		self.h = 6.6260755e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0*pi * 1e-7


	def init_data(self):
		"""Initilize the data

		The structure of self.input_info is as follows:  The fields of the first dimension correspond
		to each relaxation data set and is flexible in size, ie len(self.input_info) = number of data sets.
		The second dimension have the following fixed fields:
			0 - Data type (R1, R2, or NOE)
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

		self.input_info = []
		self.relax_data = []
		self.num_data_sets = 0
		self.runs = []

		self.stage = '0'

		self.data = {}
		self.results = []
