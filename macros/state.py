from data import data
from os import F_OK, access

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
		self.load = x.load
		self.save = x.save


class macro_class(generic_functions):
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

		relax> state_load('save')
		relax> state_load(file_name='save')


		FIN
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

		file_name:	The file name, which must be a string, to save the current program
			state in.
		force:		A flag which if set to 1 will cause the file to be overwritten.


		Examples
		~~~~~~~~

		The following commands will save the current program state into the file 'save'.

		relax> state_save('save')
		relax> state_save(file_name='save')


		If the file 'save' already exists, the following commands will save the current
		program state by overwriting the file.

		relax> state_save('save', 1)
		relax> state_save(file_name='save', force=1)


		FIN
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
