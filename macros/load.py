from re import match

from generic_functions import generic_functions


class load(generic_functions):
	def __init__(self, relax):
		"Class containing macros for loading data."

		self.relax = relax


	def init_data(self):
		"Initialise the relaxation data structures."

		# The number of relaxation data points.
		self.relax.data.num_ri = 1

		# The number of field strengths.
		self.relax.data.num_frq = 1

		# Labels corresponding to the data type.
		#	eg ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
		self.relax.data.ri_labels = [self.ri_label]

		# A translation table to map relaxation data points to their frequencies.
		self.relax.data.remap_table = [0]

		# A translation table to direct the NOE data points to the R1 data points.  Used to speed up calculations by avoiding the recalculation of R1 values.
		#	eg [None, None, 0, None, None, 3]
		self.relax.data.noe_r1_table = [None]

		# The NMR frequency labels.
		#	eg ['600', '500']
		self.relax.data.frq_labels = [self.frq_label]

		# The NMR frequencies in Hz.
		#	eg [600.0 * 1e6, 500.0 * 1e6]
		self.relax.data.frq = [self.frq]

		# The structure of self.relax.data.relax_data is as follows:  The first dimension corresponds to each
		# relaxation data point.  The fields point to 2D data structures containing the data from
		# the relaxation file (missing the single header line), ie:
		#	[res][0] - Residue number
		#	[res][1] - Residue name
		#	[res][2] - Relaxation value
		#	[res][3] - Relaxation error
		self.relax.data.relax_data = []


	def relax_data(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
		"Macro for loading R1, R2, or NOE relaxation data."

		# Arguments
		self.ri_label = ri_label
		self.frq_label = frq_label
		self.frq = frq
		self.file_name = file_name
		self.num_col = num_col
		self.name_col = name_col
		self.data_col = data_col
		self.error_col = error_col
		self.sep = sep

		# Test if sequence data is loaded.
		if not self.sequence_data_test(): return

		# Test if all arguments are supplied correctly.
		if self.test_args():
			return

		# Extract the data from the file.
		file_data = self.relax.file_ops.extract_data(self.file_name)

		# Do nothing if the file does not exist.
		if not file_data:
			print "No relaxation data loaded."
			return

		# Strip data.
		file_data = self.relax.file_ops.strip(file_data)

		# Test if relaxation data has already been loaded.
		try:
			self.relax.data.relax_data

		# Data initialisation.
		except AttributeError:
			self.init_data()

		# Update data.
		else:
			# Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
			for i in range(self.relax.data.num_ri):
				if self.ri_label == self.relax.data.ri_labels[i] and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
					print "The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been loaded."
					print "To load the data, either delete the original or use different labels."
					return

			self.update_data()

		# Add the relaxation data to self.relax.data.relax_data
		data = []
		for i in range(len(file_data)):
			data.append([int(file_data[i][self.num_col]), file_data[i][self.name_col], float(file_data[i][self.data_col]), float(file_data[i][self.error_col])])
		self.relax.data.relax_data.append(self.create_data(data))


	def sequence(self, file_name=None, num_col=0, name_col=1, sep=None):
		"Macro for loading sequence data."

		# Arguments
		self.file_name = file_name
		self.num_col = num_col
		self.name_col = name_col
		self.sep = sep

		# Test if the file name is given.
		if not file_name:
			print "No file is specified."
			return

		# Test if the sequence data has already been loaded.
		try:
			self.relax.data.seq
		except AttributeError:
			"Do nothing."
		else:
			print "The sequence data has already been loaded."
			print "To reload, delete the original sequence data (self.relax.data.seq)."
			return

		# Extract the data from the file.
		file_data = self.relax.file_ops.extract_data(self.file_name)

		# Do nothing if the file does not exist.
		if not file_data:
			print "No sequence data loaded."
			return

		# Strip data.
		file_data = self.relax.file_ops.strip(file_data)

		# Place the data in self.relax.data.seq
		seq = []
		for i in range(len(file_data)):
			try:
				seq.append([int(file_data[i][self.num_col]), file_data[i][self.name_col]])
			except ValueError:
				print "Sequence data is invalid."
				return
		self.relax.data.seq = seq


	def test_args(self):
		"Test if the arguments are correct."

		if not self.ri_label or type(self.ri_label) != str:
			print "The relaxation label 'ri_label' has not been supplied correctly."
			return 1
		elif not self.frq_label or type(self.frq_label) != str:
			print "The frequency label 'frq_label' has not been supplied correctly."
			return 1
		elif not self.frq or type(self.frq) != float:
			print "The frequency 'frq' has not been supplied correctly."
			return 1
		elif not self.file_name:
			print "No file given."
			return 1


	def update_data(self):
		"Update the relaxation data structures."

		# Update the number of relaxation data points.
		self.relax.data.num_ri = self.relax.data.num_ri + 1

		# Add ri_label to the data types.
		self.relax.data.ri_labels.append(self.ri_label)

		# Find if the frequency self.frq has already been loaded.
		remap = len(self.relax.data.frq)
		flag = 0
		for i in range(len(self.relax.data.frq)):
			if self.frq == self.relax.data.frq[i]:
				remap = i
				flag = 1

		# Update the data structures which have a length equal to the number of field strengths.
		if not flag:
			self.relax.data.num_frq = self.relax.data.num_frq + 1
			self.relax.data.frq_labels.append(self.frq_label)
			self.relax.data.frq.append(self.frq)

		# Update the remap table.
		self.relax.data.remap_table.append(remap)

		# Update the NOE R1 translation table.
		self.relax.data.noe_r1_table.append(None)
		if self.ri_label == 'NOE':
			# If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been loaded.
			for i in range(self.relax.data.num_ri):
				if self.relax.data.ri_labels[i] == 'R1' and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
					self.relax.data.noe_r1_table[self.relax.data.num_ri - 1] = i
		if self.ri_label == 'R1':
			# If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been loaded.
			for i in range(self.relax.data.num_ri):
				if self.relax.data.ri_labels[i] == 'NOE' and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
					self.relax.data.noe_r1_table[i] = self.relax.data.num_ri - 1
