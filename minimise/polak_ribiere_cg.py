from Numeric import dot

from generic_conjugate_gradient import generic_conjugate_gradient
from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class polak_ribiere(generic_conjugate_gradient, generic_line_search, generic_minimise):
	def __init__(self, func, dfunc=None, args=(), x0=None, line_search_algor=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.1):
		"""Polak-Ribière conjugate gradient algorithm.

		Page 121-122 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

		The algorithm is:

		Given x0
		Evaluate f0 = f(x0), g0 = g(x0)
		Set p0 = -g0, k = 0
		while g0 != 0:
			Compute ak and set xk+1 = xk + ak.pk
			Evaluate gk+1
			bk+1 = dot(gk+1, (gk+1 - gk)) / dot(gk, gk)
			pk+1 = -gk+1 + bk+1.pk
			k = k + 1
		"""

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


	def calc_bk(self):
		"Function to calcaluate the Polak-Ribière beta value"

		# Calculate beta at k+1.
		return dot(self.dfk_new, self.dfk_new - self.dfk) / self.dot_dfk
