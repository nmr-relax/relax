from Numeric import Float64, copy, dot, identity, matrixmultiply, outerproduct

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

		# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse hessian matrix.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk = identity(len(self.xk), Float64)

		# Set the Identity matrix I.
		self.I = identity(len(self.xk), Float64)

		# Minimisation.
		self.minimise = self.generic_minimise


	def backup_current_data(self):
		"Function to backup the current data into fk_last, xk_last, dfk_last, and d2fk_last."

		self.fk_last = self.fk
		self.xk_last = copy.deepcopy(self.xk)
		self.dfk_last = copy.deepcopy(self.dfk)
		self.d2fk_last = copy.deepcopy(self.d2fk)


	def dir(self):
		"Calculate the BFGS direction."

		self.pk = -matrixmultiply(self.d2fk, self.dfk)


	def update_data(self):
		"Function to update the function value, gradient vector, and the BFGS matrix"

		self.xk = copy.deepcopy(self.xk_new)
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1

		# BFGS matrix update.
		sk = self.xk - self.xk_last
		yk = self.dfk - self.dfk_last
		if dot(yk, sk) == 0:
			raise NameError, "The BFGS matrix is indefinite.  This should not occur."

		rk = 1.0 / dot(yk, sk)

		a = self.I - rk*outerproduct(sk, yk)
		b = self.I - rk*outerproduct(yk, sk)
		c = rk*outerproduct(sk, sk)
		matrix = matrixmultiply(matrixmultiply(a, self.d2fk), b) + c
		self.d2fk = matrix
