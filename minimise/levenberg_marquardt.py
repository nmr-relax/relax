import sys
from LinearAlgebra import solve_linear_equations
from Numeric import Float64, concatenate, zeros
from re import match

class levenberg_marquardt:
	def __init__(self, mf):
		"Levenberg-Marquardt minimisation class."
		self.mf = mf


	def fit(self, function, dfunction, function_options, chi2_func, values, errors, start_params, limits_flag, limits):
		"""Levenberg-Marquardt minimisation function.

		'function' is the function to minimise, and should return an array with the back calculated values.
		'dfunction' is the derivative function and should return an array of arrays with the first dimension corresponding
			to the values, and the second corrresponding to the derivative of the relaxation values with respect to
			function parameters.
		'function_options' are the function options to pass to 'function'.
		'values' is an array containing the values to minimise on, eg peak heights or relaxation rates.
		'errors' is an array containing the errors associated with 'values'
		'start_params' is the starting parameter values.

		The following are returned:
			1. An array with the fitted parameter values.
			2. The chi-squared value.
		"""

		self.function = function
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.values = values
		self.errors = errors
		self.params = start_params
		self.limits_flag = limits_flag
		self.limits = limits

		# Initial value of lambda (the Levenberg-Marquardt fudge factor).
		self.l = 1.0

		# Back calculate the initial function values and the chi-squared statistic.
		self.back_calc = function(self.function_options, self.params)
		self.df = dfunction(self.function_options, self.params)
		self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)

		minimise_num = 1

		# Print the status of the minimiser.
		# text = "%-4s%-6i%-8s%-46s%-6s%-25e%-8s%-6e" % ("run", 0, "Params:", `self.params`, "Chi2:", self.chi2, "l:", self.l)
		#
		# Print the status of the minimiser for model-free data (temporary code).
		if self.mf.min_debug >= 1:
			print_num = 0
			self.print_relax_crap(0)

		# Iterate until the minimiser is finished.
		while 1:
			# Print debugging info
			#if self.mf.min_debug == 2:
			#	print "\n\n"
			#	print "%-29s%-40s" % ("Minimisation run number:", `minimise_num`)

			# Calculate the Levenberg-Marquardt matrix 'self.LM_matrix' and chi-squared gradient vector 'self.chi2_grad'.
			self.create_structures()

			# Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
			param_change = solve_linear_equations(self.LM_matrix, self.chi2_grad)
			#param_change = self.gauss_jordan_elimination(self.LM_matrix, self.chi2_grad)

			# Add the current parameter vector to the parameter change vector to find the new parameter vector.
			self.new_params = []
			for i in range(len(self.params)):
				new_param = self.params[i] + param_change[i]
				if self.limits_flag == 1:
					if new_param < self.limits[i][0] or new_param > self.limits[i][1]:
						self.new_params.append(self.params[i])
					else:
						self.new_params.append(new_param)
				else:
					self.new_params.append(new_param)

			# Back calculate the new function values.
			self.back_calc = function(self.function_options, self.new_params)
			self.df = dfunction(self.function_options, self.new_params)

			# Calculate the new chi-squared statistic.
			self.chi2_new = self.chi2_func(self.values, self.back_calc, self.errors)

			# Print debugging info
			#if self.mf.min_debug == 2:
			#	for i in range(len(self.values)):
			#		print "%-29s%-40s" % ("Derivative array " + `i` + " is: ", `self.df[i]`)

			#	print "%-29s%-40s" % ("Levenberg-Marquardt matrix:", `self.LM_matrix`)
			#	print "%-29s%-40s" % ("Chi2 grad vector:", `self.chi2_grad`)
			#	print "%-29s%-40s" % ("Old parameter vector:", `self.params`)
			#	print "%-29s%-40s" % ("Parameter change vector:", `param_change`)
			#	print "%-29s%-40s" % ("New parameter vector:", `self.new_params`)
			#	print "%-29s%-40e" % ("Chi-squared:", self.chi2)
			#	print "%-29s%-40e" % ("Chi-squared new:", self.chi2_new)
			#	print "%-29s%-40e" % ("Chi-squared diff:", self.chi2 - self.chi2_new)
			#	print "%-29s%-40e" % ("l:", self.l)


			# Test improvement.
			if self.chi2_new > self.chi2:
				if self.l <= 1e99:
					self.l = self.l * 10.0
			else:
				# Finish minimising when the chi-squared difference is insignificant.
				if self.chi2 - self.chi2_new < 1e-20:
					#if self.mf.min_debug == 2:
					#	print "\n%-29s%-40e" % ("Chi-squared diff:", self.chi2 - self.chi2_new)
					#	print "%-29s%-40e" % ("Chi-squared diff limit:", 1e-10)
					#	print "Insignificant chi2 difference, stopped minimising."
					break
				if self.l >= 1e-99:
					self.l = self.l / 10.0

				# Update function parameters and chi-squared value.
				self.params = self.new_params
				self.chi2 = self.chi2_new

			# Print the status of the minimiser.
			# text = "%-4s%-6i%-8s%-46s%-6s%-25s%-8s%-6s" % ("run", minimise_num, "Params:", `self.new_params`, "Chi2:", `self.chi2_new`, "r:", `self.l`)
			#
			# Print the status of the minimiser for model-free data (temporary).
			#if self.mf.min_debug == 3:
			#	if print_num == 100:
			#		self.print_relax_crap(minimise_num)
			#		print_num = 0
			#		print_num = print_num + 1
			if self.mf.min_debug >= 1 and print_num == 1000:
				print_num = 0
				self.print_relax_crap(minimise_num)

			minimise_num = minimise_num + 1
			print_num = print_num + 1

		return self.params, self.chi2


	def print_relax_crap(self, run):
		text = "%-4s%-6i" % ("run", run)
		if match('m1', self.function_options[2]):
			text = text + "%-4s%-20g" % ("S2:", self.params[0])
		elif match('m2', self.function_options[2]):
			text = text + "%-4s%-20g" % ("S2:", self.params[0])
			text = text + "%-9s%-20g" % ("te (ps):", self.params[1]*1e12)
		elif match('m3', self.function_options[2]):
			text = text + "%-4s%-20g" % ("S2:", self.params[0])
			text = text + "%-5s%-20g" % ("Rex:", self.params[1] * self.mf.data.frq[0]**2)
		elif match('m4', self.function_options[2]):
			text = text + "%-4s%-20g" % ("S2:", self.params[0])
			text = text + "%-9s%-20g" % ("te (ps):", self.params[1]*1e12)
			text = text + "%-5s%-20g" % ("Rex:", self.params[2] * self.mf.data.frq[0]**2)
		elif match('m5', self.function_options[2]):
			text = text + "%-5s%-20g" % ("S2f:", self.params[0])
			text = text + "%-5s%-20g" % ("S2s:", self.params[1])
			text = text + "%-9s%-20g" % ("ts (ps):", self.params[2]*1e12)
		text = text + "%-6s%-25g" % ("Chi2:", self.chi2)
		text = text + "%-3s%-6g" % ("l:", self.l)
		print text


	def create_structures(self):
		"""Function to create the Levenberg-Marquardt matrix and chi-squared gradient vector.

		The Levenberg-Marquardt matrix is:

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

		The chi-squared gradient vector is:

			          _n_
			d Chi2    \   / yi - y(xi)    d y(xi) \ 
			------  =  >  | ----------  . ------- |
			  dj      /__ \ sigma_i**2      dj    /
			          i=1

			where j is one of the function parameters.
		"""

		# Create the Levenberg-Marquardt matrix and chi-squared gradient vector with elements equal to zero.
		self.LM_matrix = zeros((len(self.params), len(self.params)), Float64)
		self.chi2_grad = zeros((len(self.params)), Float64)

		# Loop over the data points from i=1 to n.
		for i in range(len(self.values)):
			# Calculate the inverse of the variance to minimise calculations.
			i_variance = 1.0 / self.errors[i]**2

			# Loop over all function parameters.
			for param_j in range(len(self.params)):
				# Calculate and sum the chi-squared gradient vector element 'param_j'.
				self.chi2_grad[param_j] = self.chi2_grad[param_j] + i_variance * (self.values[i] - self.back_calc[i]) * self.df[i, param_j]

				# Loop over the function parameters from the first to 'param_j' to create the Levenberg-Marquardt matrix.
				for param_k in range(param_j + 1):
					if param_j == param_k:
						LM_matrix_jk = i_variance * self.df[i, param_j] * self.df[i, param_k] * (1.0 + self.l)
					else:
						LM_matrix_jk = i_variance * self.df[i, param_j] * self.df[i, param_k]

					self.LM_matrix[param_j, param_k] = self.LM_matrix[param_j, param_k] + LM_matrix_jk
					self.LM_matrix[param_k, param_j] = self.LM_matrix[param_k, param_j] + LM_matrix_jk
