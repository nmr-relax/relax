from re import match


class load_seq:
	def __init__(self, relax):
		"Class containing the macro for loading sequence data."

		self.relax = relax


	def load(self, file_name=None, num_col=0, name_col=1, sep=None):
		"Macro for loading sequence data."

		# Macro intro print out.
		print "Executing macro load_seq"

		# Arguments
		self.file_name = file_name
		self.num_col = num_col
		self.name_col = name_col
		self.sep = sep

		# Test if the file name is given.
		if not file_name:
			print "No file is specified."
			print "[ failed ]"
			return

		# Macro intro print out.
		print "   File name:             " + file_name
		print "   Residue number column: " + `num_col`
		print "   Residue name column:   " + `name_col`
		if self.sep:
			print "   Seperator:             " + `sep`
		else:
			print "   Seperator:             'Whitespace'"

		# Test if the sequence data has already been loaded.
		try:
			self.relax.data.seq
		except AttributeError:
			print "Loading sequence."
		else:
			print "Sequence data is already loaded.  To reload, delete the original data."
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

		# Place the data in self.relax.data.seq
		self.relax.data.seq = []
		for i in range(len(self.file_data)):
			self.relax.data.seq.append([int(self.file_data[i][self.num_col]), self.file_data[i][self.name_col]])

		print "[ OK ]"
