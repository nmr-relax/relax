from Numeric import dot, sqrt
from trust_region import trust_region

from generic_trust_region import generic_trust_region
from generic_minimise import generic_minimise


class cauchy_point(generic_trust_region, generic_minimise):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, delta_max=1e5, delta0=1.0, eta=0.2):
		"""Cauchy Point trust-region algorithm.

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

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Initial values before the first iteration.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1

		# Minimisation.
		self.minimise = self.generic_minimise


	def backup_current_data(self):
		"Function to backup the current data into fk_last."

		self.fk_last = self.fk


	def calc_pk(self):
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


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.delta = self.delta_new
		self.xk = self.xk_new * 1.0
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
