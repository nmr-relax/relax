from LinearAlgebra import eigenvectors, inverse
from Numeric import Float64, dot, identity, matrixmultiply, outerproduct, sort, sqrt
from re import match

from bfgs import bfgs
from newton import newton
from generic_trust_region import generic_trust_region
from generic_minimise import generic_minimise


class dogleg(generic_trust_region, generic_minimise, bfgs, newton):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, min_options=(), func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, delta_max=1e10, delta0=1e5, eta=0.0001, mach_acc=1e-16):
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
		self.mach_acc = mach_acc

		self.delta_max = delta_max
		self.delta = delta0
		self.eta = eta

		# Hessian type and modification.
		self.hessian_type = None
		self.hessian_mod = None
		if type(min_options) != tuple:
			print "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1; return
		if len(min_options) > 2:
			print "A maximum of two minimisation options is allowed."
			self.init_failure = 1; return
		for opt in min_options:
			if self.hessian_type == None and (match('[Bb][Ff][Gg][Ss]', opt) or match('[Nn]ewton', opt)):
				self.hessian_type = opt
			elif self.hessian_mod == None and (opt == None or match("^[Ee]igen", opt) or match("^[Cc]hol", opt) or match("^[Gg][Mm][Ww]", opt)):
				self.hessian_mod = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is invalid."
				self.init_failure = 1; return
		if self.hessian_type == None:
			self.hessian_type = 'Newton'
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type) and self.hessian_mod != None:
			print "When using the BFGS matrix, hessian modifications should not be used."
			self.init_failure = 1; return
		if self.print_flag:
			if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
				print "Hessian type:  BFGS"
			else:
				print "Hessian type:  Newton"
			

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Hessian modification function initialisation.
		self.init_hessian_mod_funcs()


	def dogleg(self):
		"The dogleg algorithm."

		if self.print_flag == 2:
			print "Init."
			print "   delta: " + `self.delta`
			print "   xk: " + `self.xk`
			print "   fk: " + `self.fk`
			print "   dfk: " + `self.dfk`
			print "   d2fk: " + `self.d2fk`

		# Safeguarding.  Forcing the hessian to be positive definitive.
		try:
			self.Hk
		except AttributeError:
			eigen = eigenvectors(self.d2fk)
			eigenvals = sort(eigen[0])
			if eigenvals[0] <= 0.0:
				self.d2fk = self.d2fk - eigenvals[0] * identity(len(self.dfk), Float64)

		# Calculate the full step and its norm.
		try:
			pB = -matrixmultiply(self.Hk, self.dfk)
		except AttributeError:
			pB = -matrixmultiply(inverse(self.d2fk), self.dfk)
		norm_pB = sqrt(dot(pB, pB))
		if self.print_flag == 2:
			print "Full step."
			print "   pB: " + `pB`
			print "   ||pB||: " + `norm_pB`
			print "   Func value at pB is: "+ `apply(self.func, (self.xk + pB,)+self.args)`

		# Test if the full step is within the trust region.
		if norm_pB <= self.delta:
			if self.print_flag == 2:
				print "   Taking the full step, ||pB|| <= delta, " + `norm_pB` + " <= " + `self.delta`
			return pB
		if self.print_flag == 2:
			print "   Not taking the full step, ||pB|| > delta, " + `norm_pB` + " > " + `self.delta`

		# Calculate pU.
		curv = dot(self.dfk, dot(self.d2fk, self.dfk))
		pU = - dot(self.dfk, self.dfk) / curv * self.dfk
		dot_pU = dot(pU, pU)
		norm_pU = sqrt(dot_pU)
		if self.print_flag == 2:
			print "pU step."
			print "   pU: " + `pU`
			print "   ||pU||: " + `norm_pU`
			print "   Func value at pU is: "+ `apply(self.func, (self.xk + pU,)+self.args)`

		# Test if the step pU exits the trust region.
		if norm_pU >= self.delta:
			if self.print_flag == 2:
				print "   ||pU|| >= delta, " + `norm_pU` + " >= " + `self.delta`
			return self.delta * pU / norm_pU
		if self.print_flag == 2:
			print "   ||pU|| < delta, " + `norm_pU` + " < " + `self.delta`
			
		# Find the solution to the scalar quadratic equation.
		pB_pU = pB - pU
		dot_pB_pU = dot(pB_pU, pB_pU)
		dot_pU_pB_pU = dot(pU, pB_pU)
		fact = dot_pU_pB_pU**2 - dot_pB_pU * (dot_pU - self.delta**2)
		tau = (-dot_pU_pB_pU + sqrt(fact)) / dot_pB_pU
		if self.print_flag == 2:
			print "Quadratic solution."
			print "   tau: " + `tau`

		# Decide on which part of the trajectory to take.
		return pU + tau * pB_pU


	def hessian_update_bfgs(self):
		"BFGS hessian update."

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

		# Calculate the Hessian.
		self.d2fk = inverse(self.Hk)


	def hessian_update_newton(self):
		"Empty function."

		pass


	def new_param_func(self):
		"Find the dogleg minimiser."

		self.pk = self.dogleg()
		self.xk_new = self.xk + self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1

		if self.print_flag == 2:
			print "Fin."
			print "   pk:     " + `self.pk`
			print "   xk:     " + `self.xk`
			print "   xk_new: " + `self.xk_new`
			print "   fk:     " + `self.fk`
			print "   fk_new: " + `self.fk_new`


	def setup(self):
		"""Setup function.

		"""

		# Type specific functions.
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
			self.setup_bfgs()
			self.specific_update = self.update_bfgs
			self.hessian_update = self.hessian_update_bfgs
			self.d2fk = inverse(self.Hk)
		elif match('[Nn]ewton', self.hessian_type):
			self.setup_newton()
			self.specific_update = self.update_newton
			self.hessian_update = self.hessian_update_newton
		else:
			raise NameError, "Matrix type " + `self.hessian_type` + " invalid for dogleg minimisation."


	def update(self):
		"""Update function.

		Run the trust region update.  If this update decides to shift xk+1 to xk, then run
		the BFGS or Newton updates.
		"""

		self.trust_region_update()

		if not self.shift_flag:
			self.hessian_update()
		else:
			self.specific_update()
