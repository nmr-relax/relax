from Numeric import array


class load_state:
	def __init__(self, relax):
		"Class containing the macro for loading a saved program state."

		self.relax = relax


	def load(self, file_name=None):
		"Macro for loading a saved program state."

		# Macros intro print out.
		print "Executing macro load_state."

		# Arguments.
		self.file_name = file_name

		# Test arguments
		if type(file_name) != str:
			print "File name is invalid."
			print "[ failed ]"
			return

		# Open file for reading.
		try:
			file = open(file_name, 'r')
		except IOError:
			print "Save file does not exist."
			print "[ failed ]"
			return

		# Execute the file to reload all data.
		exec(file)

		print "[ OK ]"
