from LinearAlgebra import inverse
from Numeric import dot, matrixmultiply, sqrt
from trust_region import trust_region

from generic_trust_region import generic_trust_region
from generic_minimise import generic_minimise


class dogleg(generic_trust_region, generic_minimise):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, hessian_type=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, delta_max=1e5, delta0=1.0, eta=0.2):
		"""Dogleg trust-region algorithm.

		Page 71 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
		The dogleg method is defined by the trajectory p(tau):

			          / tau . pU			0 <= tau <= 1,
			p(tau) = <
			          \ pU + (tau - 1)(pB - pU),	1 <= tau <= 2.

		where:
			tau is in [0, 2]
			pU is the unconstrained minimiser along the steepest descent direction.
			pB is the full step.

		pU is defined by the formula:

			        gT.g
			pU = - ------ g
			       gT.B.g

		and pB by the formula:

			pB = - B^(-1).g

		If the full step is within the trust region it is taken.  Otherwise the point at which the dogleg
		trajectory intersects the trust region is taken.  This point can be found by solving the scalar
		quadratic equation:
			||pU + (tau - 1)(pB - pU)||^2 = delta^2

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

		# Calculate the full step and its norm.
		pB = -matrixmultiply(inverse(self.d2fk), self.dfk)
		norm_pB = sqrt(dot(pB, pB))
		if self.print_flag == 2:
			print "The full step (pB) is: " + `pB`

		# Test if the full step is within the trust region.
		if norm_pB <= self.delta:
			if self.print_flag == 2:
				print "Taking the full step"
			self.pk = pB
			return
		if self.print_flag == 2:
			print "Not taking the full step"

		# Calculate pU.
		curv = dot(self.dfk, dot(self.d2fk, self.dfk))
		norm_g = sqrt(dot(self.dfk, self.dfk))
		pU = - norm_g / curv * self.dfk
		if self.print_flag == 2:
			print "pU: " + `pU`
			print "\tFunc value at xk is: "+ `apply(self.func, (self.xk,)+self.args)`
			print "\tFunc value at pB is: "+ `apply(self.func, (self.xk + pB,)+self.args)`
			print "\tFunc value at pU is: "+ `apply(self.func, (self.xk + pU,)+self.args)`

		# Find the solution to the scalar quadratic equation.
		pB_pU = pB - pU
		norm_pB_pU_sqrd = dot(pB_pU, pB_pU)
		pUT_pB_pU = dot(pU, pB_pU)
		tau = - pUT_pB_pU + sqrt(pUT_pB_pU**2 - norm_pB_pU_sqrd * (dot(pU, pU) - self.delta**2))
		tau = tau / norm_pB_pU_sqrd + 1.0
		if self.print_flag == 2:
			print "tau: " + `tau`

		# Decide on which part of the trajectory to take.
		if tau >= 0 and tau <= 1:
			self.pk = tau * pU
		elif tau >= 1 and tau <= 2:
			self.pk = pU + (tau - 1.0)* pB_pU
		else:
			raise NameError, "Invalid value of tau."


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.delta = self.delta_new
		self.xk = self.xk_new * 1.0
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
