import sys
from LinearAlgebra import solve_linear_equations
from Numeric import copy, Float64, concatenate, zeros
from re import match

class levenberg_marquardt:
	def __init__(self, mf):
		"Levenberg-Marquardt minimisation class."
		self.mf = mf


	def fit(self, chi2_func, dchi2_func, dfunc, params, errors, args=(), tol=1e-5, maxiter=1000, full_output=0):
		"""Levenberg-Marquardt minimisation function.

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
		self.params = params
		self.errors = errors
		warning_flag = 0

		# Initial value of lambda (the Levenberg-Marquardt fudge factor).
		self.l = 1.0

		# Get some data structures.
		self.chi2 = apply(self.chi2_func, (self.params,)+args)
		self.dchi2 = -0.5 * apply(self.dchi2_func, (self.params,)+args)
		self.df = self.dfunc()

		minimise_num = 1

		# Print the status of the minimiser.
		if self.mf.min_debug >= 1:
			text = "%-4s%-6i%-8s%-46s%-6s%-25e%-8s%-6e" % ("run", 0, "Params:", `self.params`, "Chi2:", self.chi2, "l:", self.l)
			print text
		
		# Print the status of the minimiser.
		if self.mf.min_debug >= 1:
			print_num = 0

		# Iterate until the minimiser is finished.
		while 1:
			# Create the Levenberg-Marquardt matrix.
			self.lm_matrix = self.create_lm_matrix()

			# Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
			param_change = solve_linear_equations(self.lm_matrix, self.dchi2)

			# Add the current parameter vector to the parameter change vector to find the new parameter vector.
			self.new_params = zeros((len(self.params)), Float64)
			self.new_params = self.params + param_change

			# Recalculate the chi2 statistic.
			self.chi2_new = apply(self.chi2_func, (self.new_params,)+args)
			self.dchi2 = -0.5 * apply(self.dchi2_func, (self.params,)+args)
			self.df = self.dfunc()

			# Print debugging info
			if self.mf.min_debug >= 2:
				print "\n\n"
				print "%-29s%-40s" % ("Minimisation run number:", `minimise_num`)
				for i in range(len(self.errors)):
					print "%-29s%-40s" % ("Derivative array " + `i` + " is: ", `self.df[:,i]`)

				print "%-29s%-40s" % ("Levenberg-Marquardt matrix:", `self.lm_matrix`)
				print "%-29s%-40s" % ("Chi2 grad vector:", `self.dchi2`)
				print "%-29s%-40s" % ("Old parameter vector:", `self.params`)
				print "%-29s%-40s" % ("Parameter change vector:", `param_change`)
				print "%-29s%-40s" % ("New parameter vector:", `self.new_params`)
				print "%-29s%-40e" % ("Chi-squared:", self.chi2)
				print "%-29s%-40e" % ("Chi-squared new:", self.chi2_new)
				print "%-29s%-40e" % ("Chi-squared diff:", self.chi2 - self.chi2_new)
				print "%-29s%-40e" % ("l:", self.l)


			# Test improvement.
			if self.chi2_new > self.chi2:
				if self.l <= 1e99:
					self.l = self.l * 10.0
			else:
				# Finish minimising when the chi-squared difference is insignificant.
				if self.chi2 - self.chi2_new < tol:
					if self.mf.min_debug >= 2:
						print "\n%-29s%-40e" % ("Chi-squared diff:", self.chi2 - self.chi2_new)
						print "%-29s%-40e" % ("Chi-squared diff limit:", 1e-10)
						print "Insignificant chi2 difference, stopped minimising."
					break
				if self.l >= 1e-99:
					self.l = self.l / 10.0

				# Update function parameters and chi-squared value.
				self.params = copy.deepcopy(self.new_params)
				self.chi2 = self.chi2_new

			# Print the status of the minimiser.
			if self.mf.min_debug >= 1:
				print_num = print_num + 1
				if print_num == 1000:
					text = "%-4s%-6i%-8s%-46s%-6s%-25s%-8s%-6s" % ("run", minimise_num, "Params:", `self.new_params`, "Chi2:", `self.chi2_new`, "l:", `self.l`)
					print text
					print_num = 0
			
			# Check to see if the maximum number of iterations have been reached.
			if minimise_num >= maxiter:
				warning_flag = 1
				break

			minimise_num = minimise_num + 1

		if full_output:
			return (self.params, self.chi2, minimise_num, warning_flag)
		else:
			return (self.params, self.chi2)


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
		matrix = zeros((len(self.params), len(self.params)), Float64)

		# Loop over the error points from i=1 to n.
		for i in range(len(self.errors)):
			# Calculate the inverse of the variance to minimise calculations.
			i_variance = 1.0 / self.errors[i]**2

			# Loop over all function parameters.
			for param_j in range(len(self.params)):
				# Loop over the function parameters from the first to 'param_j' to create the Levenberg-Marquardt matrix.
				for param_k in range(param_j + 1):
					if param_j == param_k:
						matrix_jk = i_variance * self.df[param_j, i] * self.df[param_k, i] * (1.0 + self.l)
					else:
						matrix_jk = i_variance * self.df[param_j, i] * self.df[param_k, i]

					matrix[param_j, param_k] = matrix[param_j, param_k] + matrix_jk
					matrix[param_k, param_j] = matrix[param_k, param_j] + matrix_jk
		return matrix
