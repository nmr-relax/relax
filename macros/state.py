from data import data
from Numeric import array
from os import F_OK, access

from generic_functions import generic_functions


class state(generic_functions):
	def __init__(self, relax):
		"Class containing the macros for manipulating the program state."

		self.relax = relax


	def load(self, file_name=None):
		"Macro for loading a saved program state."

		# Arguments.
		self.file_name = file_name

		# Test arguments
		if type(file_name) != str:
			print "File name is invalid."
			return

		# Open file for reading.
		try:
			file = open(file_name, 'r')
		except IOError:
			print "Save file does not exist."
			return

		# Reinitialise self.relax.data
		self.relax.data = data()

		# Execute the file to reload all data.
		exec(file)


	def save(self, file_name=None, force=0):
		"Macro for saving the program state."

		# Arguments.
		self.file_name = file_name

		# Test arguments
		if type(file_name) != str:
			print "File name is invalid."
			return

		# Open file for writing.
		if access(file_name, F_OK) and not force:
			print "File already exists.  Set the force flag to 1 to overwrite."
			return
		else:
			file = open(file_name, 'w')

		# Loop over the data structures in self.relax.data
		for name in dir(self.relax.data):
			if not self.filter_data_structure(name):
				file.write("self.relax.data." + name + " = " + `getattr(self.relax.data, name)`)
				file.write("\n")
