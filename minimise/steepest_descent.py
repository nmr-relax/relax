from Numeric import dot

from generic import Line_search, Min


def steepest_descent(func, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.1):
	"""Steepest descent minimisation.

	"""

	min = Steepest_descent(func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta)
	if min.init_failure:
		print "Initialisation of minimisation has failed."
		return None
	results = min.minimise()
	return results


class Steepest_descent(Line_search, Min):
	def __init__(self, func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta):
		"""Class for steepest descent minimisation specific functions.

		Unless you know what you are doing, you should call the function 'steepest_descent'
		rather than using this class.
		"""

		self.func = func
		self.dfunc = dfunc
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Minimisation options.
		#######################

		# Initialise.
		self.init_failure = 0

		# Line search options.
		if not self.line_search_option(min_options):
			self.init_failure = 1
			return

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Line search function initialisation.
		self.init_line_functions()


	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		# Calculate the steepest descent direction.
		self.pk = -self.dfk

		# Update a0 using information about the last iteration.
		try:
			self.a0 = self.alpha * dot(self.dfk_last, -self.dfk_last) / dot(self.dfk, -self.dfk)
		except AttributeError:
			"First iteration."
			pass

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup(self):
		"""Setup function.

		The function value fk and gradient vector gk (dfk) are calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1


	def update(self):
		"Function to update the function value, gradient vector, and Hessian matrix"

		# Store old data.
		self.fk_last = self.fk
		self.dfk_last = self.dfk * 1.0

		# Shift k+1 data to k.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
