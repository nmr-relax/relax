from LinearAlgebra import inverse
from Numeric import matrixmultiply

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class newton(generic_line_search, generic_minimise):
	def __init__(self):
		"Class for Newton minimisation specific functions."


	def minimise(self, *min_args):
		"Newton minimisation."

		# Generic data initialisation.
		self.min_args = min_args
		self.init_data()

		# The initial Newton function value, gradient vector, and hessian matrix.
		self.update_data()

		# Set a0.
		self.a0 = 1.0

		# Line search constants for the Wolfe conditions.
		self.mu = 0.0001
		self.eta = 0.9

		# Minimisation.
		self.generic_minimise()

		if self.full_output:
			return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			return self.xk

	def dir(self):
		"Calculate the Newton direction."

		self.pk = -matrixmultiply(inverse(self.d2fk), self.dfk)


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
