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



	class init_overall_disc:
		def __init__(self):
			"Data specific for model-free analysis using the overall discrepancy."

			self.name = 'Overall'
			self.op_data = []


	class init_palmer:
		def __init__(self):
			"Data specific for Palmer's model-free analysis."

			self.name = 'Palmer'



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



	def calc_constants(self):
		"""Calculate the dipolar and CSA constants.

		Dipolar constants
		~~~~~~~~~~~~~~~~~
			      1   / mu0  \ 2  (gH.gN.h_bar)**2
			d  =  - . | ---- |  . ----------------
			      4   \ 4.pi /         <r**6>


			         3   / mu0  \ 2  (gH.gN.h_bar)**2
			d'  =  - - . | ---- |  . ----------------
			         2   \ 4.pi /         <r**7>


			       21   / mu0  \ 2  (gH.gN.h_bar)**2
			d"  =  -- . | ---- |  . ----------------
			       2    \ 4.pi /         <r**8>


		CSA constants
		~~~~~~~~~~~~~
			      (wN.csa)**2
			c  =  -----------
			           3


			       2.wN**2.csa
			c'  =  -----------
			            3


			       2.wN**2
			c"  =  -------
			          3

		"""

		self.rnh = float(self.mf.usr_param.const['rxh'])
		self.csa = float(self.mf.usr_param.const['csa'])

		# Dipolar constant.

		a = ((self.mu0/(4.0*pi)) * self.h_bar * self.gh * self.gx) ** 2
		self.dipole_const = 0.25 * a * self.rnh**-6
		self.dipole_prime = -1.5 * a * self.rnh**-7
		self.dipole_2prime = 10.5 * a * self.rnh**-8
		dip_temp = self.dipole_const / 1e9

		self.csa_const = []
		self.csa_prime = []
		self.csa_2prime = []
		csa_temp = []
		for i in range(self.num_frq):
			a = (self.frq_list[i][1]**2) / 3.0
			self.csa_const.append(a * self.csa**2)
			self.csa_prime.append(2.0 * a * self.csa)
			self.csa_2prime.append(2.0 * a)
			csa_temp.append(0.0)

		if self.mf.debug:
			print "%-20s%-20s" % ("r(NH):", `self.rnh`)
			print "%-20s%-20s" % ("CSA:", `self.csa`)
			print "%-20s%-20s" % ("CSA squared:", `self.csa**2`)
			print "%-20s%-20s" % ("gH:", `self.gh`)
			print "%-20s%-20s" % ("gN:", `self.gx`)
			print "%-20s%-20s" % ("h-bar:", `self.h_bar`)
			print "%-20s%-20s" % ("mu0:", `self.mu0`)
			print "%-20s%-20s" % ("Dipolar const / 1e9", dip_temp)
			print "%-20s%-20s" % ("CSA const / 1e9", csa_temp)
			print "\n"



	def calc_frq(self):
		"Calculate all the frequencies which lead to relaxation."

		self.frq_list = []
		self.frq_sqrd_list = []
		for i in range(self.num_frq):
			self.frq_list.append([])
			self.frq_sqrd_list.append([])

			frqH = 2.0 * pi * self.frq[i]
			frqN = frqH * ( self.gx / self.gh )

			# Normal frequencies.
			self.frq_list[i].append(0.0)
			self.frq_list[i].append(frqN)
			self.frq_list[i].append(frqH - frqN)
			self.frq_list[i].append(frqH)
			self.frq_list[i].append(frqH + frqN)
			
			# Frequencies squared.
			self.frq_sqrd_list[i].append(0.0)
			self.frq_sqrd_list[i].append(frqN**2)
			self.frq_sqrd_list[i].append((frqH - frqN)**2)
			self.frq_sqrd_list[i].append(frqH**2)
			self.frq_sqrd_list[i].append((frqH + frqN)**2)


	def init_constants(self):
		self.gh = 26.7522e7
		self.gx = -2.7126e7
		self.h = 6.6260755e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0*pi * 1e-7


	def init_data(self):
		"Initilise the data structures."

		# The number of data points.
		#	eg 6
		self.num_ri = 0

		# The number of field strengths.
		#	eg 2
		self.num_frq = 0
		
		# Labels corresponding to the data type.
		#	eg ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
		self.data_types = []

		# The names of the files containing the relaxation data.
		#	eg ['R1.out', 'R2.out', 'NOE.out', 'R1.out', 'R2.out', 'NOE.out']
		self.data_files = []

		# A translation table to map relaxation data points to their frequencies.
		#	eg [0, 0, 0, 1, 1, 1]
		self.remap_table = []

		# A translation table to direct the NOE data points to the R1 data points.  Used to speed up
		# calculations by avoiding the recalculation of R1 values.
		#	eg [None, None, 0, None, None, 3]
		self.noe_r1_table = []

		# The NMR frequency labels.
		#	eg ['600', '500']
		self.frq_label = []

		# The NMR frequencies in Hz.
		#	eg [600.0 * 1e6, 500.0 * 1e6]
		self.frq = []

		# The structure of self.relax_data is as follows:  The first dimension corresponds to each
		# relaxation data point.  The fields point to 2D data structures containing the data from
		# the relaxation file (missing the single header line), ie:
		#	[res][0] - Residue number
		#	[res][1] - Residue name
		#	[res][2] - Relaxation value
		#	[res][3] - Relaxation error
		self.relax_data = []

		# Don't know if these are used any more?
		#self.runs = []
		#self.stage = '0'
		#self.data = {}
		#self.results = []
