
class function_init:
	def __init__(self, relax):
		"Base class containing the functions used to set the functions used in minimisation."

		self.relax = relax


	def init(self, type):
		"Function used to set the functions used in minimisation."

		if match('mf', type):
			funcs = mf_trans_functions(self.relax)
			self.func = funcs.chi2
			self.dfunc = funcs.dchi2
			self.d2func = funcs.d2chi2
