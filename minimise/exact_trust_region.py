from LinearAlgebra import cholesky_decomposition, eigenvectors, inverse
from Numeric import diagonal, dot, identity, matrixmultiply, outerproduct, sort, sqrt, transpose
from re import match

from newton import newton
from generic_trust_region import generic_trust_region
from generic_minimise import generic_minimise


class exact_trust_region(generic_trust_region, generic_minimise, newton):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, lambda0=10.0, delta_max=1e5, delta0=1.0, eta=0.2):
		"""Exact trust region algorithm.

		Page 77-87 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

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

		self.lambda0 = lambda0
		self.delta_max = delta_max
		self.delta = delta0
		self.eta = eta

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None


	def new_param_func(self):
		"Find the exact trust region solution."

		# Calculate the newton step and its norm.
		pB = -matrixmultiply(inverse(self.d2fk), self.dfk)
		norm_pB = sqrt(dot(pB, pB))

		# Debugging code.
		self.xk_new = self.xk * 1.0
		self.fk_new = self.fk

		# Test if the newton step is inside the trust region and, if so, accept the step.
		if norm_pB <= self.delta:
			if self.print_flag == 2:
				print "Taking the full step: " + `pB`
			self.pk = pB
		else:
			if self.print_flag == 2:
				print "Not taking the full step: " + `pB`

			# The exact trust region algorithm.
			l = 0
			self.lambda_l = self.lambda0
			self.I = identity(len(self.dfk))
			eigen = eigenvectors(self.d2fk)
			eigenvals = sort(eigen[0])
			if self.print_flag == 2:
				print "Eigenvalues: " + `eigenvals`

			while l < 3:
				# Safeguard.
				if self.print_flag == 2:
					print "l: " + `l` + ", lambda(l) orig: " + `self.lambda_l`
				self.safeguard(eigenvals)

				# Calculate the matrix B + lambda(l).I
				matrix = self.d2fk + self.lambda_l * self.I

				# Factor B + lambda(l).I = RT.R
				R = cholesky_decomposition(matrix)

				# Solve pl = -inverse(RT.R).g
				pl = -matrixmultiply(inverse(matrix), self.dfk)

				# Solve ql = inverse(RT).pl
				ql = matrixmultiply(inverse(transpose(R)), pl)

				# Lengths
				dot_pl = dot(pl, pl)

				# lambda(l+1) update.
				self.lambda_l = self.lambda_l + dot_pl / dot(ql, ql) * ((sqrt(dot_pl) - self.delta) / self.delta)

				if self.print_flag == 2:
					print "\tl: " + `l` + ", lambda(l) fin: " + `self.lambda_l`

				l = l + 1

			self.pk = -matrixmultiply(inverse(self.d2fk + self.lambda_l * self.I), self.dfk) 

			if self.print_flag == 2:
				print "Step: " + `self.pk`

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def safeguard(self, eigenvals):
		"Safeguarding function."

		if self.lambda_l < -eigenvals[0]:
			self.lambda_l = -eigenvals[0] + 1.0
			if self.print_flag == 2:
				print "\tSafeguarding. lambda(l) = " + `self.lambda_l`
		elif self.lambda_l <= 0.0:
			if self.print_flag == 2:
				print "\tSafeguarding. lambda(l)=0"
			self.lambda_l = 0.0


	def setup(self):
		"""Setup function.

		"""

		self.setup_newton()
		self.specific_update = self.update_newton


	def update(self):
		"""Update function.

		Run the trust region update.  If this update decides to shift xk+1 to xk, then run
		the Newton update.
		"""

		self.trust_region_update()
		if self.shift_flag:
			self.specific_update()
