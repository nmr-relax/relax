from Numeric import dot, sqrt

from generic import Trust_region, Min


def cauchy_point(func, dfunc=None, d2func=None, args=(), x0=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, delta_max=1e5, delta0=1.0, eta=0.2):
	"""Cauchy Point trust region algorithm.

	Page 69 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	The Cauchy point is defined by:

		                 delta
		pCk  =  - tau_k ------- dfk
		                ||dfk||

	where:
		delta_k is the trust region radius,
		dfk is the gradient vector,

		         / 1						if dfk . Bk . dfk <= 0
		tau_k = <
		         \ min(||dfk||**2/(delta . dfk . Bk . dfk), 1)	otherwise.
	"""

	min = Cauchy_point(func, dfunc, d2func, args, x0, func_tol, maxiter, full_output, print_flag, delta_max, delta0, eta)
	results = min.minimise()
	return results


class Cauchy_point(Trust_region, Min):
	def __init__(self, func, dfunc, d2func, args, x0, func_tol, maxiter, full_output, print_flag, delta_max, delta0, eta):
		"""Class for Cauchy Point trust region minimisation specific functions.

		Unless you know what you are doing, you should call the function 'cauchy_point'
		rather than using this class.
		"""

		self.func = func
		self.dfunc = dfunc
		self.d2func = d2func
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		self.delta_max = delta_max
		self.delta = delta0
		self.eta = eta

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None


	def new_param_func(self):
		"Find the Cauchy point."

		# Calculate the curvature and norm.
		curv = dot(self.dfk, dot(self.d2fk, self.dfk))
		norm_dfk = sqrt(dot(self.dfk, self.dfk))

		# tau_k.
		if curv <= 0.0:
			self.tau_k = 1.0
		else:
			self.tau_k = min(norm_dfk ** 3 / (self.delta * curv), 1.0)

		if self.print_flag == 2:
			print "dfk . Bk . dfk: " + `curv`
			print "tau_k:          " + `self.tau_k`

		# Cauchy point.
		self.pk = - self.tau_k * self.delta * self.dfk / norm_dfk

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup(self):
		"""Setup function.

		"""

		# Initial values before the first iteration.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


	def update(self):
		"""Update function.

		Function to update the function value, gradient vector, and Hessian matrix
		"""

		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
