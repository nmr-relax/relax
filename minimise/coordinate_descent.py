from Numeric import Float64, dot, identity

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class coordinate_descent(generic_line_search, generic_minimise):
	def __init__(self, func, dfunc=None, args=(), x0=None, line_search_algor=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.1):
		"Class for back-and-forth coordinate descent minimisation specific functions."

		self.func = func
		self.dfunc = dfunc
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		if not line_search_algor:
			raise NameError, "No line search algorithm has been supplied."
		else:
			self.line_search_algor = line_search_algor

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# The initial function value and gradient vector.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1

		# Create the coordinate descent directions, and initialise the coordinate descent iteration number and direction flag.
		self.cd_dir = identity(len(self.xk), Float64)
		self.n = 0
		self.back = 0

		# Minimisation.
		self.minimise = self.generic_minimise


	def backup_current_data(self):
		"Function to backup the current data dfk into dfk_last."

		self.fk_last = self.fk
		self.dfk_last = self.dfk * 1.0


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


	def get_a0(self):
		"Update a0 using information about the last iteration."

		self.a0 = self.alpha * dot(self.dfk_last, -self.dfk_last) / dot(self.dfk, -self.dfk)


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.xk = self.xk_new * 1.0
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
