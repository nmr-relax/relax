from generic_functions import generic_functions
from value_setup import value_setup


class bond_length(generic_functions, value_setup):
	def __init__(self, relax):
		"Class containing the macro for setting bond length values."

		self.relax = relax


	def get_data(self):
		"Initialise the bond length specific data."

		try:
			self.data = self.relax.data.bond_length
		except AttributeError:
			self.data = None

		self.string = "bond length"
		self.macro_name = "bond_length"


	def get_load_data(self):
		"Initialise the load_bond_length specific data."

		try:
			self.data = self.relax.data.bond_length
		except AttributeError:
			self.data = None

		self.string = "load bond length"
		self.macro_name = "load_bond_length"
