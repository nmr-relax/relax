from value_setup import value_setup


class csa(value_setup):
	def __init__(self, relax):
		"Class containing the macro for setting csa values."

		self.relax = relax


	def get_data(self):
		"Initialise the csa specific data."

		try:
			self.data = self.relax.data.csa
		except AttributeError:
			self.data = None

		self.string = "CSA"
		self.macro_name = "csa"


	def get_load_data(self):
		"Initialise the load_csa specific data."

		try:
			self.data = self.relax.data.csa
		except AttributeError:
			self.data = None

		self.string = "load CSA"
		self.macro_name = "load_csa"


	def init_data(self):
		self.relax.data.csa = []
		self.data = self.relax.data.csa


