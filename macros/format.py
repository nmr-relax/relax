from re import match
import sys

from generic_functions import generic_functions
from select_res import select_res


class format(generic_functions, select_res):
	def __init__(self, relax):
		"Macros for printing data to standard out."

		self.relax = relax


	def format(self, *args):
		"""Macro to print the names of all data structures in self.relax.data

		With no arguments, the names of all data structures in self.relax.data are printed
		along with the data type.


		FIN
		"""

		self.args = args

		# Print the names of all data structures in self.relax.data if no arguments are given.
		if len(self.args) == 0:
			print "Data structures:"
			for name in dir(self.relax.data):
				if not self.filter_data_structure(name):
					print "   " + name + " " + `type(getattr(self.relax.data, name))`
			return

		# Sort out the arguments.
		self.struct = self.args[0]
		self.sel = self.args[1:]

		# Test if the data structure exists.
		try:
			getattr(self.relax.data, self.struct)
		except AttributeError:
			print "Data structure 'self.relax.data." + self.struct + "' does not exist."
			return

		# Sequence data.
		if self.struct == 'seq':
			# Test if sequence data is loaded.
			try:
				self.relax.data.seq
			except AttributeError:
				print "No sequence data loaded."
				return
			self.indecies = self.select_residues()
			if not self.indecies:
				return
			self.print_data(self.relax.data.seq, seq_flag=1)

		# Relaxation data.
		#elif self.struct == 'relax_data':
		#	self.print_data(self.relax.data.seq, seq_flag=0)

		# Other data.
		else:
			print "Data structure " + self.struct + ":"
			print `getattr(self.relax.data, self.struct)`


	def print_data(self, data, seq_flag=0):
		"Macro to print data according to the argument list given."

		if seq_flag:
			print "%-5s%-5s" % ("num", "name")
		else:
			print "%-5s%-5s%-20s%-20s" % ("num", "name", "data", "errors")

		for index in self.indecies:
			if seq_flag:
				print "%-5i%-5s" % (data[index][0], data[index][1])
			else:
				print "%-5i%-5s%-20e%-20e" % (data[index][0], data[index][1], data[index][2], data[index][3])
