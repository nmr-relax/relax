from select_res import select_res


class value_setup(select_res):
	def __init__(self):
		"Base class containing functions for the setting up of data structures."


	def load(self, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
		"Macro for loading data structure values from file."

		# Arguments
		self.file_name = file_name
		self.num_col = num_col
		self.name_col = name_col
		self.data_col = data_col
		self.error_col = error_col
		self.sep = sep

		# Get the load macro specific data.
		self.get_load_data()

		# Test if the file name is given.
		if not file_name:
			print "No file is specified."
			print "[ failed ]"
			return

		# Macro intro print out.
		print "Executing macro load_csa"
		print "   File name:             " + self.file_name
		print "   Residue number column: " + `self.num_col`
		print "   Residue name column:   " + `self.name_col`
		print "   Data column:           " + `self.data_col`
		print "   Error column:          " + `self.error_col`
		if self.sep:
			print "   Seperator:             " + `self.sep`
		else:
			print "   Seperator:             'Whitespace'"

		# Test if sequence data is loaded.
		try:
			self.relax.data.seq
		except AttributeError:
			print "Sequence data has to be loaded first."
			print "[ failed ]"
			return

		# Test if the data has already been loaded.
		if self.data:
			print "Data structure already exists."
			print "[ failed ]"
			return

		# Extract the data from the file.
		self.file_data = self.relax.file_ops.extract_data(self.file_name)

		# Do nothing if the file does not exist.
		if not self.file_data:
			print "No sequence data loaded."
			print "[ failed ]"
			return

		# Strip data.
		self.file_data = self.relax.file_ops.strip(self.file_data)

		# Place the data in self.relax.data.csa:
		self.init_data()
		for i in range(len(self.file_data)):
			self.data.append([float(self.file_data[i][self.data_col]), float(self.file_data[i][self.error_col])])

		print "[ OK ]"


	def set(self, *args):
		"Macro for setting data structure values."

		# Arguments.
		self.args = args
		self.sort_args()

		# Get the specific data.
		self.get_data()

		# Macro intro print out.
		print "Executing macro " + self.macro_name
		print "   " + self.string + " of all residues set to " + `self.val`

		# Test if sequence data is loaded.
		try:
			self.relax.data.seq
		except AttributeError:
			print "Sequence data has to be loaded first."
			print "[ failed ]"
			return

		if len(self.args) == 0:
			print "No arguments given. Cannot set up data structure."
			print "[ failed ]"
			return

		# Set one value to all residues.
		if len(self.sel) == 0:
			if self.data:
				print "Data structure already exists."
				print "[ failed ]"
				return

			self.init_data()
			for i in range(len(self.relax.data.seq)):
				self.data.append([self.val, self.err])


		# Set fixed values to specific residues.
		else:
			if not self.data:
				self.init_data()
				for i in range(len(self.relax.data.seq)):
					self.data.append([None, None])

			self.indecies = self.select_residues()
			if not self.indecies:
				print "[ failed ]"
				return
			print "data: " + `self.data`
			for index in self.indecies:
				self.data[index][0] = self.val
				self.data[index][1] = self.err

		print "[ OK ]"


	def sort_args(self):
		"Sort the arguments."

		self.sel = []
		self.val = None
		self.err = None
		for i in range(len(self.args)):
			if type(self.args[i]) == int or type(self.args[i]) == str:
				self.sel.append(self.args[i])
			elif not self.val:
				self.val = self.args[i]
			elif not self.err:
				self.err = self.args[i]
			else:
				print "Arguments not set correctly."
				return
