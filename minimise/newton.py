from LinearAlgebra import inverse
from Numeric import copy, dot, matrixmultiply

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class newton(generic_line_search, generic_minimise):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, line_search_algor=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9):
		"Class for Newton minimisation specific functions."

		self.func = func
		self.dfunc = dfunc
		self.d2func = d2func
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

		# The initial Newton function value, gradient vector, and hessian matrix.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1

		# Minimisation.
		self.minimise = self.generic_minimise


	def backup_current_data(self):
		"Function to backup the current data into fk_last."

		self.fk_last = self.fk


	def dir(self):
		"Calculate the Newton direction."

		print "dfk: " + `self.dfk`
		print "d2fk: " + `self.d2fk`
		self.pk = -matrixmultiply(inverse(self.d2fk), self.dfk)
		if dot(self.dfk, self.pk) >= 0.0:
			self.pk = -self.dfk


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.xk = copy.deepcopy(self.xk_new)
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
