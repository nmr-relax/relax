from LinearAlgebra import solve_linear_equations
from Numeric import Float64, zeros

from generic_minimise import generic_minimise


class levenberg_marquardt(generic_minimise):
	def __init__(self):
		"Class for Levenberg-Marquardt minimisation specific functions."


	def minimise(self, chi2_func, dchi2_func, dfunc, errors, x0, args=(), func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
		"""Levenberg-Marquardt minimisation.

		Function options
		~~~~~~~~~~~~~~~~

		chi2_func:  User supplied chi-squared function which is run with the function parameters and args as options.
		dchi2_func:  User supplied chi-squared gradient function which is run with the function parameters and args as options.
		dfunc:  User supplied function which should return a vector of partial derivatives of the function which back calculates
			values for the chi-squared function.
		params:  The initial function parameter values.
		errors:  The experimental errors.
		args:  A tuple containing the arguments to send to chi2_func and dchi2_func.
		maxiter:  The maximum number of iterations.
		full_output:  A flag specifying what should be returned.


		Output
		~~~~~~

		If full_output = 0, the parameter values and chi-squared value are returned as a tuple.
		If full_output = 1, the parameter values, chi-squared value, number of iterations, and the warning flag are returned as a tuple.

		"""

		self.chi2_func = chi2_func
		self.dchi2_func = dchi2_func
		self.dfunc = dfunc
		self.errors = errors
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

		# The initial Newton function value, gradient vector, and hessian matrix.
		self.update_data()

		# Initial value of lambda (the Levenberg-Marquardt fudge factor).
		self.l = 1.0
		self.n = len(self.xk)

		# Minimisation.
		self.generic_minimise()

		if self.full_output:
			return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			return self.xk


	def create_lm_matrix(self):
		"""Function to create the Levenberg-Marquardt matrix.

		The matrix is:

			               _n_
			               \   /     1        d y(xi)   d y(xi)                \ 
			LM_matrix_jk =  >  | ---------- . ------- . ------- . (1 + lambda) |
			               /__ \ sigma_i**2     dj        dk                   /
			               i=1

			where j == k is one of the function parameters.

			               _n_
			               \   /     1        d y(xi)   d y(xi) \ 
			LM_matrix_jk =  >  | ---------- . ------- . ------- |
			               /__ \ sigma_i**2     dj        dk    /
			               i=1

			where j != k are function parameters.
		"""

		# Create the Levenberg-Marquardt matrix with elements equal to zero.
		self.lm_matrix = zeros((self.n, self.n), Float64)

		# Loop over the error points from i=1 to n.
		for i in range(len(self.errors)):
			# Calculate the inverse of the variance to minimise calculations.
			i_variance = 1.0 / self.errors[i]**2

			# Loop over all function parameters.
			for param_j in range(self.n):
				# Loop over the function parameters from the first to 'param_j' to create the Levenberg-Marquardt matrix.
				for param_k in range(param_j + 1):
					if param_j == param_k:
						matrix_jk = i_variance * self.df[param_j, i] * self.df[param_k, i] * (1.0 + self.l)
					else:
						matrix_jk = i_variance * self.df[param_j, i] * self.df[param_k, i]

					self.lm_matrix[param_j, param_k] = self.lm_matrix[param_j, param_k] + matrix_jk
					self.lm_matrix[param_k, param_j] = self.lm_matrix[param_k, param_j] + matrix_jk


	def new_param_func(self):
		"Find the new parameter vector self.xk_new"

		# Create the Levenberg-Marquardt matrix.
		self.create_lm_matrix()

		# Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
		self.param_change = solve_linear_equations(self.lm_matrix, self.dfk)

		# Add the current parameter vector to the parameter change vector to find the new parameter vector.
		xk_new = zeros(self.n, Float64)
		xk_new = self.xk + self.param_change

		return xk_new


	def tests(self):
		"Levenberg-Marquardt tests."

		if self.fk > self.fk_last:
			if self.l <= 1e99:
				self.l = self.l * 10.0
		else:
			# Finish minimising when the chi-squared difference is insignificant.
			if abs(self.fk_last - self.fk) < self.func_tol:
				return 1
			if self.l >= 1e-99:
				self.l = self.l / 10.0
		return 0


	def update_data(self):
		"Function to update the chi-squared value, chi-squared gradient vector, and derivative function matrix."

		self.fk, self.f_count = apply(self.chi2_func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = -0.5 * apply(self.dchi2_func, (self.xk,)+self.args), self.g_count + 1
		self.df = self.dfunc()
