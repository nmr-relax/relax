from Numeric import copy, dot

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class steepest_descent(generic_line_search, generic_minimise):
	def __init__(self):
		"Class for steepest descent minimisation specific functions."


	def minimise(self, *min_args):
		"Steepest descent minimisation."

		# Generic data initialisation.
		self.min_args = min_args
		self.init_data()

		# The initial function value and gradient vector.
		self.update_data()

		# Set a0.
		self.a0 = 1.0

		# Line search constants for the Wolfe conditions.
		self.mu = 0.0001
		self.eta = 0.1

		# Minimisation.
		self.generic_minimise()

		if self.full_output:
			return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			return self.xk


	def backup_current_data(self):
		"Function to backup the current data dfk into dfk_last."

		self.dfk_last = copy.deepcopy(self.dfk)


	def dir(self):
		"Return the steepest descent direction."

		self.pk = -self.dfk


	def get_a0(self):
		"Update a0 using information about the last iteration."

		self.a0 = self.alpha * dot(self.dfk_last, -self.dfk_last) / dot(self.dfk, -self.dfk)


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk = None
