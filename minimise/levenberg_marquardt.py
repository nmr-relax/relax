import sys
from re import match

class levenberg_marquardt:
	def __init__(self, mf):
		"Levenberg-Marquardt minimisation class."
		self.mf = mf


	def fit(self, function, dfunction, function_options, chi2_func, values, data_points, errors, start_params):
		"""Levenberg-Marquardt minimisation function.

		'function' is the function to minimise, and should return a single value.
		'dfunction' is the derivative of the function 'function', and should return an array with the elements corresponding
			to the 'function' parameters.
		'function_options' are the function options to pass to 'function' and 'dfunction'.
		'values' is an array containing the values to minimise on, eg peak heights or relaxation rates.
		'data_points' is an array containing information on type corresponding to 'values', eg relaxation time or relaxation data type.
		'errors' is an array containing the errors associated with 'values'
		'start_params' is the starting parameter values.

		The following are returned:
			1. An array with the fitted parameter values.
			2. The chi-squared value.


		"""

		self.function = function
		self.dfunction = dfunction
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.values = values
		self.data_points = data_points
		self.errors = errors
		self.params = start_params

		# Initial value of lambda (the Levenberg-Marquardt fudge factor).
		self.l = 1.0

		# Back calculate the initial function values and the chi-squared statistic.
		self.back_calc = []
		for i in range(len(self.data_points)):
			self.back_calc.append(function(self.function_options, self.data_points[i], self.params))
		self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)

		minimise_num = 1

		# Print the status of the minimiser.
		# text = "%-4s%-6i%-8s%-46s%-6s%-25e%-8s%-6e" % ("run", 0, "Params:", `self.params`, "Chi2:", self.chi2, "l:", self.l)
		#
		# Print the status of the minimiser for model-free data (temporary code).
		print_num = 0
		self.print_relax_crap(0)

		while 1:
			# Calculate the Levenberg-Marquardt matrix 'self.LM_matrix' and chi-squared gradient vector 'self.chi2_grad'.
			self.LM_matrix, self.chi2_grad = self.create_structures()

			# Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
			param_change = self.gauss_jordan_elimination(self.LM_matrix, self.chi2_grad)

			# Add the current parameter vector to the parameter change vector to find the new parameter vector.
			self.new_params = []
			for i in range(len(self.params)):
				self.new_params.append(self.params[i] + param_change[i])

			# Back calculate the new function values.
			self.back_calc = []
			for i in range(len(self.data_points)):
				self.back_calc.append(function(self.function_options, self.data_points[i], self.new_params))

			# Calculate the new chi-squared statistic.
			self.chi2_new = self.chi2_func(self.values, self.back_calc, self.errors)

			# Print debugging info
			if self.mf.min_debug == 1:
				print "\n\nMinimisation run number " + `minimise_num`
				print "Levenberg-Marquardt matrix: " + `self.LM_matrix`
				print "Chi2 grad vector: " + `self.chi2_grad`
				print "Old parameter vector: " + `self.params`
				print "Parameter change vector: " + `param_change`
				print "New parameter vector: " + `self.new_params`
				print "Chi-squared: " + `self.chi2`
				print "Chi-squared new: " + `self.chi2_new`
				print "l: " + `self.l`


			# Test improvement.
			if self.chi2_new >= self.chi2:
				if self.l <= 1e99:
					self.l = self.l * 10.0
			else:
				# Finish minimising when the chi-squared difference is zero.
				if self.chi2 - self.chi2_new < 1e-3:
					print "chi2 diff: " + `self.chi2 - self.chi2_new`
					print "No chi2 difference, stopped minimising."
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
			#if print_num == 100:
			self.print_relax_crap(minimise_num)
			#	print_num = 0

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
			text = text + "%-5s%-20g" % ("Rex:", self.params[1])
		elif match('m4', self.function_options[2]):
			text = text + "%-4s%-20g" % ("S2:", self.params[0])
			text = text + "%-9s%-20g" % ("te (ps):", self.params[1]*1e12)
			text = text + "%-5s%-20g" % ("Rex:", self.params[2])
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
		LM_matrix = []
		chi2_grad = []
		for j in range(len(self.params)):
			LM_matrix.append([])
			chi2_grad.append(0.0)
			for k in range(len(self.params)):
				LM_matrix[j].append(0.0)

		# Loop over the data points from i=1 to n.
		for i in range(len(self.values)):
			# Calculate the inverse of the variance to minimise calculations.
			i_variance = 1.0 / self.errors[i]**2

			# Calculate the function derivative array for the data point 'i'.
			df = self.dfunction(self.function_options, self.data_points[i], self.params)
			if self.mf.min_debug == 1:
				print "The derivative array is: " + `df`

			# Loop over all function parameters.
			for param_j in range(len(self.params)):
				# Calculate and sum the chi-squared gradient vector element 'j'.
				chi2_grad[param_j] = chi2_grad[param_j] + i_variance * (self.values[i] - self.back_calc[i]) * df[param_j]

				# Loop over the function parameters from the first to 'j' to create the Levenberg-Marquardt matrix.
				for param_k in range(param_j + 1):
					if param_j == param_k:
						LM_matrix_jk = i_variance * df[param_j] * df[param_k] * (1.0 + self.l)
					else:
						LM_matrix_jk = i_variance * df[param_j] * df[param_k]

					LM_matrix[param_j][param_k] = LM_matrix[param_j][param_k] + LM_matrix_jk
					LM_matrix[param_k][param_j] = LM_matrix[param_k][param_j] + LM_matrix_jk

		return LM_matrix, chi2_grad


	def elementary_row_operations(self, A, i):
		"""Row reduce by Gauss-Jordan elimination.

		'A' is the augmented matrix to row reduce.
		'i' is the index of the row to work with.

		The function does the following 3 elementary row operations:
			1. Interchange two rows.
			2. Set A[i][i] to 1 by dividing row[i] by A[i][i].
			3. Eliminate the terms A[row][i] where row != i.
		"""

		num_rows = len(A)
		num_cols = len(A[0])

		# Step 1.
		#########
		# Test if rows need to be switched, ie if 'A[i][i]' is 0 and there is a row below in which the column 'i' has a non-zero element.
		if A[i][i] == 0:
			# Loop over the rows below row i.
			for j in range(i,num_rows):
				# Check if A[j][i] has a non-zero element.
				if A[j][i] != 0:
					switch_row = A[i]
					A[i] = A[j]
					A[j] = switch_row
					break

		# If unsuccessful, don't do the steps below and just return the unmodified matrix.
		if A[i][i] == 0:
			return A

		if self.mf.min_debug == 1:
			print "\tA pre norm: " + `A`

		# Step 2.
		#########
		# Make 'A[i][i]' equal to 1 by looping over the columns of the row 'i' and dividing by 'A[i][i]'.
		coeff = A[i][i]
		for col in range(num_cols):
			A[i][col] = A[i][col] / coeff

		if self.mf.min_debug == 1:
			print "\tA norm: " + `A`

		# Step 3.
		#########
		# Eliminate the 'A[row][i]' terms in the other rows.
		for row in range(num_rows):
			# If the row is i, skip the elimination step.
			if row == i:
				continue
			# Subtract the row 'i' multiplied by the term 'A[row][i]' from the row 'row'
			coeff = A[row][i]
			for col in range(num_cols):
				A[row][col] = A[row][col] - coeff * A[i][col]

		if self.mf.min_debug == 1:
			print "\tA sub: " + `A`

		return A


	def gauss_jordan_elimination(self, A, b):
		"""Solves the system of linear equations Ax = b by Gauss-Jordan elimination.

		'A' is the coefficient matrix.
		'b' is a vector.
		'x' is the returned solution vector.
		"""

		len_A = len(A)

		# Construct the augmented matrix [A|b].
		Ab = []
		for row in range(len_A):
			Ab.append([])
			for col in range(len(A[row])):
				Ab[row].append(A[row][col])
			Ab[row].append(b[row])
		if self.mf.min_debug == 1:
			print "Ab: " + `Ab`

		# Row reduce the matrix.
		for i in range(len_A):
			Ab = self.elementary_row_operations(Ab, i)

		# Extract the result vector 'x'.
		x = []
		for row in range(len(Ab)):
			x.append(Ab[row][-1])

		return x
