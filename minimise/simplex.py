import sys

from Numeric import Float64, add, argsort, average, take, zeros

from generic_minimise import generic_minimise


class simplex(generic_minimise):
	def __init__(self, func, args=(), x0=None, func_tol=1e-5, maxiter=None, full_output=0, print_flag=0):
		"Class for downhill simplex minimisation specific functions."

		self.func = func
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None


	def new_param_func(self):
		"""The new parameter function.
		
		Simplex movement.
		"""

		self.reflect_flag = 1
		self.shrink_flag = 0

		self.pivot_point = average(self.simplex[:-1])

		self.reflect()
		if self.reflect_val <= self.simplex_vals[0]:
			self.extend()
		elif self.reflect_val >= self.simplex_vals[-2]:
			self.reflect_flag = 0
			if self.reflect_val < self.simplex_vals[-1]:
				self.contract()
			else:
				self.contract_orig()
		if self.reflect_flag:
			self.simplex[-1], self.simplex_vals[-1] = self.reflect_vector, self.reflect_val
		if self.shrink_flag:
			self.shrink()

		self.order_simplex()

		self.xk_new = self.simplex[0]
		self.fk_new = self.simplex_vals[0]


	def contract(self):
		"Contraction step."

		self.contract_vector = 1.5 * self.pivot_point - 0.5 * self.simplex[-1]
		self.contract_val, self.f_count = apply(self.func, (self.contract_vector,)+self.args), self.f_count + 1
		if self.contract_val < self.reflect_val:
			self.simplex[-1], self.simplex_vals[-1] = self.contract_vector, self.contract_val
		else:
			self.shrink_flag = 1


	def contract_orig(self):
		"Contraction of the original simplex."

		self.contract_orig_vector = 0.5 * (self.pivot_point + self.simplex[-1])
		self.contract_orig_val, self.f_count = apply(self.func, (self.contract_orig_vector,)+self.args), self.f_count + 1
		if self.contract_orig_val < self.simplex_vals[-1]:
			self.simplex[-1], self.simplex_vals[-1] = self.contract_orig_vector, self.contract_orig_val
		else:
			self.shrink_flag = 1


	def extend(self):
		"Extension step."

		self.extend_vector = 3.0 * self.pivot_point - 2.0 * self.simplex[-1]
		self.extend_val, self.f_count = apply(self.func, (self.extend_vector,)+self.args), self.f_count + 1
		if self.extend_val < self.reflect_val:
			self.simplex[-1], self.simplex_vals[-1] = self.extend_vector, self.extend_val
			self.reflect_flag = 0


	def order_simplex(self):
		"Order the vertecies of the simplex according to accending function values."
		sorted = argsort(self.simplex_vals)
		self.simplex = take(self.simplex, sorted)
		self.simplex_vals = take(self.simplex_vals, sorted)


	def reflect(self):
		"Reflection step."

		self.reflect_vector = 2.0 * self.pivot_point - self.simplex[-1]
		self.reflect_val, self.f_count = apply(self.func, (self.reflect_vector,)+self.args), self.f_count + 1


	def setup(self):
		"""Setup function.

		This function initialises some constants and creates the initial simplex.
		"""

		# Initialise some constants.
		self.n = len(self.xk)
		self.m = self.n + 1

		# Create the simplex
		self.simplex = zeros((self.m, self.n), Float64)
		self.simplex_vals = zeros(self.m, Float64)

		self.simplex[0] = self.xk
		self.simplex_vals[0], self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1

		for i in range(self.n):
			j = i + 1
			self.simplex[j] = self.xk
			if self.xk[i] == 0.0:
				self.simplex[j, i] = 2.5 * 1e-4
			else:
				self.simplex[j, i] = 1.05 * self.simplex[j, i]
			self.simplex_vals[j], self.f_count = apply(self.func, (self.simplex[j],)+self.args), self.f_count + 1

		# Order the simplex.
		self.order_simplex()

		# Set xk and fk as the vertex of the simplex with the lowest function value.
		self.xk = self.simplex[0]
		self.fk = self.simplex_vals[0]


	def shrink(self):
		"Shrinking step."

		for i in range(self.n):
			j = i + 1
			self.simplex[j] = 0.5 * (self.simplex[0] + self.simplex[j])
			self.simplex_vals[j], self.f_count = apply(self.func, (self.simplex[j],)+self.args), self.f_count + 1


	def tests(self):
		"""Convergence test.

		Finish minimising when the function difference between the highest and lowest
		simplex vertecies is insignificant.
		"""

		if abs(self.simplex_vals[-1] - self.simplex_vals[0]) < self.func_tol:
			return 1
