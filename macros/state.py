from data import data
from Numeric import array
from os import F_OK, access

from generic_functions import generic_functions


class state(generic_functions):
	def __init__(self, relax):
		"Class containing the macros for manipulating the program state."

		self.relax = relax


	def load(self, file_name=None):
		"""Macro for loading a saved program state.

		Arguments
		~~~~~~~~~

		file_name:	The file name, which must be a string, of a saved program state.


		Examples
		~~~~~~~~

		The following commands will load the state saved in the file 'save'.

		>>> state_load('save')
		>>> state_load(file_name='save')

		"""

		# Arguments.
		self.file_name = file_name

		# Test arguments
		if type(file_name) != str:
			print "The file name argument " + `file_name` + " is not a string."
			return

		# Open file for reading.
		try:
			file = open(file_name, 'r')
		except IOError:
			print "The save file " + `file_name` + " does not exist."
			return

		# Reinitialise self.relax.data
		self.relax.data = data()

		# Execute the file to reload all data.
		exec(file)


	def save(self, file_name=None, force=0):
		"""Macro for saving the program state.

		Arguments
		~~~~~~~~~

		file_name:	The file name, which must be a string, to save the current program state in.
		force:		A flag which if set to 1 will cause the file to be overwritten.


		Examples
		~~~~~~~~

		The following commands will save the current program state into the file 'save'.

		>>> state_save('save')
		>>> state_save(file_name='save')


		If the file 'save' already exists, the following commands will save the current program state by overwriting
		the file.

		>>> state_save('save', 1)
		>>> state_save(file_name='save', force=1)

		"""

		# Arguments.
		self.file_name = file_name

		# Test arguments
		if type(file_name) != str:
			print "The file name argument " + `file_name` + " is not a string."
			return

		# Open file for writing.
		if access(file_name, F_OK) and not force:
			print "The file " + `file_name` + " already exists.  Set the force flag to 1 to overwrite."
			return
		else:
			file = open(file_name, 'w')

		# Loop over the data structures in self.relax.data
		for name in dir(self.relax.data):
			if not self.filter_data_structure(name):
				file.write("self.relax.data." + name + " = " + `getattr(self.relax.data, name)`)
				file.write("\n")
