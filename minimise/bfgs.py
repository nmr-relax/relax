from Numeric import Float64, dot, identity, matrixmultiply, outerproduct, sum

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class bfgs(generic_line_search, generic_minimise):
	def __init__(self, func, dfunc=None, args=(), x0=None, line_search_algor=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9):
		"Class for Quasi-Newton BFGS minimisation specific functions."

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

		# Set the setup and update functions.
		self.setup = self.setup_bfgs
		self.update = self.update_bfgs


	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		# Calculate the BFGS direction.
		self.pk = -matrixmultiply(self.Hk, self.dfk)

		# Take a steepest descent step if self.pk is not a descent dir.
		if dot(self.dfk, self.pk) >= 0.0:
			print "Step: " + `self.k` + ".  Switching to a steepest descent step to avoid an ascent direction."
			self.pk = -self.dfk

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup_bfgs(self):
		"""Setup function.
		
		Create the identity matrix I and calculate the function, gradient and initial BFGS
		inverse hessian matrix.
		"""

		# Set the Identity matrix I.
		self.I = identity(len(self.xk), Float64)

		# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse hessian matrix.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.Hk = self.I * 1.0


	def update_bfgs(self):
		"Function to update the function value, gradient vector, and the BFGS matrix"

		self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

		# BFGS matrix update.
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

		# Shift xk+1 data to xk.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk = self.dfk_new * 1.0
