from LinearAlgebra import inverse
from Numeric import dot, matrixmultiply


class generic_conjugate_gradient:
	def __init__(self):
		"Class containing the non-specific conjugate gradient code."


	def new_param_func(self):
		"""The new parameter function.

		Do a line search then calculate xk+1, fk+1, and gk+1.
		"""

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
		self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

		if self.print_flag == 2:
			print "New param func:"
			print "\tLine search algor: " + self.line_search_algor
			print "\ta:    " + `self.alpha`
			print "\tpk:   " + `self.pk`
			print "\txk:   " + `self.xk`
			print "\txk+1: " + `self.xk_new`
			print "\tfk:   " + `self.fk`
			print "\tfk+1: " + `self.fk_new`
			print "\tgk:   " + `self.dfk`
			print "\tgk+1: " + `self.dfk_new`


	def setup(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and Hessian matrix are calculated.
		"""
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.pk = -self.dfk
		self.dot_dfk = dot(self.dfk, self.dfk)


	def tests(self):
		"Convergence tests."

		inf_norm = 0.0
		for i in range(len(self.dfk)):
			inf_norm = max(inf_norm, abs(self.dfk[i]))
		if inf_norm < 1e-10 * (1.0 + abs(self.fk)):
			self.warning = "Gradient tol reached."
			return 1
		elif abs(self.fk_new - self.fk) == 0.0:
			self.warning = "Function tol of zero reached."
			return 1
		else:
			return 0


	def update(self):
		"Function to update the function value, gradient vector, and Hessian matrix"

		# Gradient dot product at k+1.
		self.dot_dfk_new = dot(self.dfk_new, self.dfk_new)

		# Calculate beta at k+1.
		bk_new = self.calc_bk()

		# Restarts.
		if abs(dot(self.dfk_new, self.dfk)) / self.dot_dfk_new >= 0.1:
			if self.print_flag == 2:
				print "Restarting."
			bk_new = 0

		# Calculate pk+1.
		self.pk_new = -self.dfk_new + bk_new * self.pk

		if self.print_flag == 2:
			print "Update func:"
			print "\tpk:     " + `self.pk`
			print "\tpk+1:   " + `self.pk_new`

		# Update.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk = self.dfk_new * 1.0
		self.pk = self.pk_new * 1.0
		self.dot_dfk = self.dot_dfk_new
