from LinearAlgebra import inverse
from Numeric import dot, matrixmultiply, outerproduct, sqrt
from re import match

from bfgs import bfgs
from newton import newton
from generic_trust_region import generic_trust_region
from generic_minimise import generic_minimise


class dogleg(generic_trust_region, generic_minimise, bfgs, newton):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, hessian_type=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, delta_max=1e5, delta0=1.0, eta=0.2):
		"""Dogleg trust region algorithm.

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

		# Matrix type.
		if hessian_type == None:
			self.hessian_type = 'bfgs'
		else:
			self.hessian_type = hessian_type

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None


	def get_pB_bfgs(self):
		"Get the newton full step."

		return -matrixmultiply(self.Hk, self.dfk)


	def get_pB_newton(self):
		"Get the newton full step."

		return -matrixmultiply(inverse(self.d2fk), self.dfk)


	def hessian_update(self):
		"BFGS hessian update."

		try:
			self.Hk
		except AttributeError:
			return

		# BFGS matrix update.
		self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1
		sk = self.xk_new - self.xk
		yk = self.dfk_new - self.dfk
		if dot(yk, sk) == 0:
			raise NameError, "The BFGS matrix is indefinite.  This should not occur."
			rk = 1e99
		else:
			rk = 1.0 / dot(yk, sk)

		if self.k == 0:
			self.Hk = dot(yk, sk) / dot(yk, yk) * self.I

		a = self.I - rk*outerproduct(sk, yk)
		b = self.I - rk*outerproduct(yk, sk)
		c = rk*outerproduct(sk, sk)
		matrix = matrixmultiply(matrixmultiply(a, self.Hk), b) + c
		self.Hk = matrix


	def new_param_func(self):
		"Find the dogleg minimiser."

		# Calculate the full step and its norm.
		pB = self.get_pB()
		norm_pB = sqrt(dot(pB, pB))

		# Debugging.
		try:
			temp = dot(pB, dot(self.Hk, pB))
		except AttributeError:
			temp = dot(pB, dot(inverse(self.d2fk), pB))
		if temp <= 0.0:
			self.warning = "The model is not convex, dogleg minimisation has failed."
			self.xk_new = self.xk * 1.0
			self.fk_new = self.fk
			return
		if self.print_flag == 2:
			print "xk: " + `self.xk`
			print "fk: " + `self.fk`
			print "dfk: " + `self.dfk`
			print "d2fk: " + `self.d2fk`
			print "The full step (pB) is: " + `pB`

		# Test if the full step is within the trust region.
		if norm_pB <= self.delta:
			if self.print_flag == 2:
				print "Taking the full step"
			self.pk = pB
		else:
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
			fact = pUT_pB_pU**2 - norm_pB_pU_sqrd * (dot(pU, pU) - self.delta**2)
			if fact < 0.0:
				self.warning = "No solution to the quadratic equation (minimisation failure)."
				return
			else:
				tau = - pUT_pB_pU + sqrt(fact)
			tau = tau / norm_pB_pU_sqrd + 1.0
			if self.print_flag == 2:
				print "tau: " + `tau`

			# Decide on which part of the trajectory to take.
			if tau >= 0 and tau <= 1:
				self.pk = tau * pU
			elif tau >= 1 and tau <= 2:
				self.pk = pU + (tau - 1.0)* pB_pU
			else:
				raise NameError, "Invalid value of tau: " + `tau`

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup(self):
		"""Setup function.

		"""

		# Type specific functions.
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
			self.setup_bfgs()
			self.specific_update = self.update_bfgs
			self.get_pB = self.get_pB_bfgs
			self.d2fk = inverse(self.Hk)
		elif match('[Nn]ewton', self.hessian_type):
			self.setup_newton()
			self.specific_update = self.update_newton
			self.get_pB = self.get_pB_newton
		else:
			raise NameError, "Matrix type " + `self.hessian_type` + " invalid for dogleg minimisation."


	def update(self):
		"""Update function.

		Run the trust region update.  If this update decides to shift xk+1 to xk, then run
		the BFGS or Newton updates.
		"""

		self.trust_region_update()
		if self.k == 0 and self.shift_flag == 0:
			self.hessian_update()

		if self.shift_flag:
			self.specific_update()

		try:
			self.d2fk = inverse(self.Hk)
		except AttributeError:
			pass
