from re import match
import types


class generic_functions:
	def __init__(self):
		"Base class containing generic functions used by many macros."


	def filter_data_structure(self, name):
		"""Function to filter out unwanted data structures from self.relax.data

		If name is unwanted, 1 is returned, otherwise 0 is returned.
		"""

		if match("__", name):
			return 1
		elif type(getattr(self.relax.data, name)) == types.ClassType:
			return 1
		elif type(getattr(self.relax.data, name)) == types.InstanceType:
			return 1
		elif type(getattr(self.relax.data, name)) == types.MethodType:
			return 1
		elif type(getattr(self.relax.data, name)) == types.NoneType:
			return 1
		else:
			return 0


	def sequence_data_test(self):
		"Test if sequence data is loaded."

		try:
			self.relax.data.seq
			return 1
		except AttributeError:
			print "Sequence data has to be loaded first."
			print "[ failed ]"
			return 0
