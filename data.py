from math import pi


class data:
	def __init__(self):
		"""Class containing all the program data.

		"""

		self.gh = 26.7522e7
		#self.gh = 26.7522212e7
		self.gx = -2.7126e7
		self.g_ratio = self.gh / self.gx
		self.h = 6.6260755e-34
		#self.h = 6.62606876e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0 * pi * 1e-7

		# The sequence data.
		#self.seq = []

		# The number of data points, eg 6.
		#self.num_ri = 0

		# The number of field strengths, eg 2.
		#self.num_frq = 0

		# Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1', 'R2']
		#self.ri_labels = []

		# A translation table to map relaxation data points to their frequencies, eg [0, 0, 0, 1, 1, 1]
		#self.remap_table = []

		# A translation table to direct the NOE data points to the R1 data points.  Used to speed up
		# calculations by avoiding the recalculation of R1 values.  eg [None, None, 0, None, None, 3]
		#self.noe_r1_table = []

		# The NMR frequency labels, eg ['600', '500']
		#self.frq_labels = []

		# The NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
		#self.frq = []

		# The structure of self.relax_data is as follows:  The first dimension corresponds to each
		# relaxation data point.  The fields point to 2D data structures containing the data from
		# the relaxation file (missing the single header line), ie:
		#	[res][1] - Relaxation value
		#	[res][2] - Relaxation error
		#	[res][3] - Flag, 0 = no data, 1 = data.
		#self.relax_data = []

		# The model equations.
		#self.equations = {}

		# The model parameters.
		#self.param_types = {}

		# The model parameter values.
		#self.params = {}

		# The model parameter errors.
		#self.param_errors = {}

		# The diagonal scaling vectors.
		#self.scaling = {}
