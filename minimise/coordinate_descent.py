from Numeric import Float64, copy, dot, identity

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class coordinate_descent(generic_line_search, generic_minimise):
	def __init__(self):
		"Class for back-and-forth coordinate descent minimisation specific functions."


	def minimise(self, *min_args):
		"Back-and-forth coordinate descent minimisation."

		# Generic data initialisation.
		self.min_args = min_args
		self.init_data()

		# The initial function value and gradient vector.
		self.update_data()

		# Set a0.
		self.a0 = 1.0

		# Create the coordinate descent directions, and initialise the coordinate descent iteration number and direction flag.
		self.cd_dir = identity(len(self.xk), Float64)
		self.n = 0
		self.back = 0

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
		"Return  the back-and-forth coordinate search direction for iteration k."

		# The direction pk is forced to be a descent direction.
		if dot(self.dfk, self.cd_dir[self.n]) > 0.0:
			self.pk = -self.cd_dir[self.n]
		else:
			self.pk = self.cd_dir[self.n]

		# Update the coordinate descent iteration number and direction flag.
		if not self.back:
			if self.n < len(self.xk) - 1:
				self.n = self.n + 1
			else:
				self.back = 1
				self.n = self.n - 1
		else:
			if self.n > 0:
				self.n = self.n - 1
			else:
				back = 0
				self.n = self.n + 1


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk = None
