from generic_functions import generic_functions


class skin:
	def __init__(self, relax):
		"""The class accessible to the interpreter.

		The purpose of this class is to hide the variables and functions found within the
		namespace of the macro class, found below, except for those required for interactive
		use.  This is an abstraction layer designed to avoid user confusion as none of the
		macro class data structures are accessible.  For more flexibility use the macro
		class directly.
		"""

		# Load the macro class into the namespace of this __init__ function.
		x = macro_class(relax)

		# Place references to the interactive functions within the namespace of this skin class.
		self.relax_data = x.relax_data
		self.sequence = x.sequence


class macro_class(generic_functions):
	def __init__(self, relax):
		"Class containing macros for loading data."

		self.relax = relax


	def relax_data(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
		"""Macro for loading R1, R2, or NOE relaxation data.

		Arguments
		~~~~~~~~~

		ri_label:	The relaxation data type, ie 'R1', 'R2', or 'NOE'.
		frq_label:	A string to label the field strength, ie '600'.  Can be anything as
			long as data collected at the same field strength have the same label.
		frq:		The spectrometer frequency in Hz.
		file_name:	The name of the file containing the relaxation data.
		num_col:	The residue number column (the default is 0, ie the first column).
		name_col:	The residue name column (the default is 1).
		data_col:	The relaxation data column (the default is 2).
		error_col:	The experimental error column (the default is 3).
		sep:		The column separator (the default is white space).


		Examples
		~~~~~~~~

		The following commands will load the NOE relaxation data collected at 600 MHz out of
		a file called 'noe.600.out' where the residue numbers, residue names, data, errors
		are in the first, second, third, and forth columns respectively.

		relax> load_relax_data('NOE', '600', 599.7 * 1e6, 'noe.600.out')
		relax> load_relax_data(ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
		file_name='noe.600.out')


		The following commands will load the R2 data out of the file 'r2.out' where the
		residue numbers, residue names, data, errors are in the second, third, fifth, and
		sixth columns respectively.  The columns are separated by commas.

		relax> load_relax_data('R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
		relax> load_relax_data(ri_label='R2', frq_label='800 MHz', frq=8.0*1e8,
		file_name='r2.out', num_col=1, name_col=2, data_col=4, error_col=5, sep=',')


		The following commands will load the R1 data out of the file 'r1.out' where the
		columns are separated by the symbol '%'

		relax> load_relax_data('R1', '300', 300.1 * 1e6, 'r1.out', sep='%')


		FIN
		"""

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
		if not len(self.relax.data.seq):
			print "Sequence data has to be loaded first."
			return

		# Test if all arguments are supplied correctly.
		if not self.ri_label or type(self.ri_label) != str:
			print "The relaxation label 'ri_label' has not been supplied correctly."
			return
		elif not self.frq_label or type(self.frq_label) != str:
			print "The frequency label 'frq_label' has not been supplied correctly."
			return
		elif not self.frq or type(self.frq) != float:
			print "The frequency 'frq' has not been supplied correctly."
			return
		elif not self.file_name:
			print "No file given."
			return

		# Extract the data from the file.
		file_data = self.relax.file_ops.extract_data(self.file_name)

		# Do nothing if the file does not exist.
		if not file_data:
			print "No relaxation data loaded."
			return

		# Strip data.
		file_data = self.relax.file_ops.strip(file_data)

		# Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
		for i in range(self.relax.data.num_ri):
			if self.ri_label == self.relax.data.ri_labels[i] and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
				print "The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been loaded."
				print "To load the data, either delete the original or use different labels."
				return

		# Update the data.
		self.update_data()

		# Add the relaxation data to self.relax.data.relax_data
		data = []
		for i in range(len(file_data)):
			data.append([int(file_data[i][self.num_col]), file_data[i][self.name_col], float(file_data[i][self.data_col]), float(file_data[i][self.error_col])])
		self.relax.data.relax_data.append(self.create_data(data))


	def sequence(self, file_name=None, num_col=0, name_col=1, sep=None):
		"""Macro for loading sequence data.

		Arguments
		~~~~~~~~~

		file_name:	The name of the file containing the sequence data.
		num_col:	The residue number column (the default is 0, ie the first column).
		name_col:	The residue name column (the default is 1).
		sep:		The column separator (the default is white space).


		Examples
		~~~~~~~~

		The following commands will load the sequence data out of a file called 'seq' where
		the residue numbers and names are in the first and second columns respectively.

		relax> load_sequence('seq')
		relax> load_sequence('seq', 0, 1)
		relax> load_sequence('seq', 0, 1, None)
		relax> load_sequence('seq', num_col=0, name_col=1)
		relax> load_sequence(file_name='seq', num_col=0, name_col=1, seq=None)


		The following commands will load the sequence out of the file 'noe.out' which also
		contains the NOE values.

		relax> load_sequence('noe.out')
		relax> load_sequence('noe.out', 0, 1)


		The following commands will load the sequence out of the file 'noe.600.out' where
		the residue numbers are in the second column, the names are in the sixth column and
		the columns are separated by commas.

		relax> load_sequence('noe.600.out', 1, 5, ',')
		relax> load_sequence(file_name='noe.600.out', num_col=1, name_col=5, seq=',')


		FIN
		"""

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
		if len(self.relax.data.seq) > 0:
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
