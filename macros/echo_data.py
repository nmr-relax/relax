from re import match
import sys

from generic_functions import generic_functions
from select_res import select_res


class echo_data(generic_functions, select_res):
	def __init__(self, relax):
		"Macros for printing data to standard out."

		self.relax = relax


	def echo(self, *args):
		"""Macro to print the names of all data structures in self.relax.data

		With no arguments, the names of all data structures in self.relax.data are printed
		along with the data type.


		FIN
		"""

		self.args = args

		# Print the names of all data structures in self.relax.data if no arguments are given.
		if len(self.args) == 0:
			print dir(self.relax.data)
			return

		for struct in args:
			# Test if the data structure exists.
			try:
				getattr(self.relax.data, struct)
			except AttributeError:
				print "Data structure 'self.relax.data." + struct + "' does not exist."
				continue

			print `getattr(self.relax.data, struct)`


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
