from Numeric import Float64, copy, dot, identity, matrixmultiply, outerproduct

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class bfgs(generic_line_search, generic_minimise):
	def __init__(self):
		"Class for Quasi-Newton BFGS minimisation specific functions."


	def minimise(self, *min_args):
		"Quasi-Newton BFGS minimisation."

		# Generic data initialisation.
		self.min_args = min_args
		self.init_data()

		# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse hessian matrix.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk = identity(len(self.xk), Float64)

		# Set a0 and the Identity matrix I.
		self.a0 = 1.0
		self.I = identity(len(self.xk), Float64)

		# Line search constants for the Wolfe conditions.
		self.mu = 0.0001
		self.eta = 0.9

		# Minimisation.
		self.generic_minimise()

		if self.full_output:
			return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			return self.xk


	def backup_current_data(self):
		"Function to backup the current data into xk_last, dfk_last, and d2fk_last."
		self.xk_last = copy.deepcopy(self.xk)
		self.dfk_last = copy.deepcopy(self.dfk)
		self.d2fk_last = copy.deepcopy(self.d2fk)


	def dir(self):
		"Calculate the BFGS direction."

		self.pk = -matrixmultiply(self.d2fk, self.dfk)


	def update_data(self):
		"Function to update the function value, gradient vector, and the BFGS matrix"

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
