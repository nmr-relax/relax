import sys

class levenberg_marquardt:
	def __init__(self, mf):
		"Levenberg-Marquardt minimisation class."
		self.mf = mf


	def calc(self, mf, function, dfunction, function_options, chi2_func, values, types, errors, start_params):
		"""Levenberg-Marquardt minimisation function.

		'function' is the function to minimise, and should return a single value.
		'dfunction' is the derivative of the function 'function', and should return an array with the elements corresponding
			to the 'function' parameters.
		'function_options' are the function options to pass to 'function' and 'dfunction'.
		'values' is an array containing the values to minimise on, eg peak heights or relaxation rates.
		'types' is an array containing information on type corresponding to 'values', eg relaxation time or relaxation data type.
		'errors' is an array containing the errors associated with 'values'
		'start_params' is the starting parameter values.

		The following are returned:
			1. An array with the fitted parameter values.
			2. The chi-squared value.


		The derivative of the chi-squared statistic is:

                                     __n__
			d Chi2       \     yi - y(xi)   d y(xi)
			------  = -2  >    ---------- . -------
			  dx         /____  sigma**2      dx   
                                     i = 1

		"""

		self.function = function
		self.dfunction = dfunction
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.values = values
		self.types = types
		self.errors = errors
		self.params = start_params

		# Initial value of r.
		self.r = 0.001

		# Back calculate the initial function values.
		self.back_calc = []
		for i in range(len(self.types)):
			self.back_calc.append(function(self.function_options, self.types[i], self.params))

		# Calculate the chi-squared statistic.
		self.chi2_old = self.chi2_func(self.values, self.back_calc, self.errors)
		self.chi2 = self.chi2_old * 10.0   # All we need is self.chi2/self.chi2_old > 1.01

		# Array containing the chi-squared derivatives with respect to the parameters.
		#self.dchi2 = []
		#for param in range(len(self.params)):
		#	self.dchi2.append(-self.chi2_derivatives(param)/2)

		minimise_num = 1
		print "%-4s%-6i%-8s%-46s%-6s%-25e%-8s%-6e" % ("run", minimise_num, "Params:", `self.params`, "Chi2:", self.chi2_old, "r:", self.r)
		while 1:
			if self.mf.min_debug == 1:
				print "\n\nMinimisation run number " + `minimise_num`

			# Calculate the coefficient matrix.
			if self.mf.min_debug == 1:
				print "Solving coeff_matrix."
			self.create_structures()
			if self.mf.min_debug == 1:
				print "Matrix A: " + `self.A`
				print "Vector beta: " + `self.beta`
				print "[ done ]\n"

			# ???
			if self.mf.min_debug == 1:
				print "Linear solve."
			dpar = self.linear_solve(self.A, self.beta)
			if self.mf.min_debug == 1:
				print "[ done ]\n"

			# Vector addition.
			if self.mf.min_debug == 1:
				print "Vector addition."
			if len(self.params) != len(dpar):
				print "Vectors not the same size!"
				sys.exit()
			new_params = []
			for i in range(len(self.params)):
				new_params.append(self.params[i] + dpar[i])
			if self.mf.min_debug == 1:
				print "new_params are: " + `new_params`
				print "[ done ]\n"

			# Back calculate the new function values.
			self.back_calc = []
			for i in range(len(self.types)):
				self.back_calc.append(function(self.function_options, self.types[i], new_params))

			# Calculate the new chi-squared statistic.
			self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)
			if self.mf.min_debug == 1:
				print "Chi-squared old: " + `self.chi2_old`
				print "Chi-squared: " + `self.chi2`
				print "r old: " + `self.r`


			# Test improvement.
			if self.chi2 <= self.chi2_old:
				self.r = self.r / 10.0
				self.params = new_params

				# Test if the chi-squared change is significant and if not, finish minimising.
				if abs(self.chi2_old - self.chi2) == 0.0:
					print "No chi2 difference, stopped minimising."
					break
				self.chi2_old = self.chi2
			else:
				self.r = self.r * 10.0
			print "%-4s%-6i%-8s%-46s%-6s%-25s%-8s%-6s" % ("run", minimise_num, "Params:", `new_params`, "Chi2:", `self.chi2`, "r:", `self.r`)

			minimise_num = minimise_num + 1

		return self.params, self.chi2


	def create_structures(self):
		"""This matrix is defined by
                       ___
		       \    /     1      df   df            \ 
		A'   =  >   | -------- . -- . --  . delta_a | 
		  jk   /__  \ sigma**2   dp   dp            / 
		                   i       j    k

		for j == k, delta_a = 1 + r
		for j != k, delta_a = 1

		r is a positive constant used to give a particular weight to
		the diagonal elements.  It's value is altered during the
		procedure.
		"""

		# Create an empty A matrix and beta vector.
		self.A = []
		self.beta = []
		for j in range(len(self.params)):
			self.A.append([])
			self.beta.append(0.0)
			for k in range(len(self.params)):
				self.A[j].append(0.0)

		if self.mf.min_debug == 1:
			print "Empty A matrix: " + `self.A`
			print "Empty beta vector: " + `self.beta`

		# Calculate the element of the symmetric matrix A.
		for i in range(len(self.values)):
			variance = self.errors[i]**2

			# Get the derivatives.
			self.df = self.dfunction(self.function_options, self.types[i], self.params)
			if self.mf.min_debug == 1:
				print "The derivative array is: " + `self.df`


			for param_j in range(len(self.params)):
				dchi2 = (self.values[i] - self.back_calc[i]) / variance * self.df[param_j]
				self.beta[param_j] = self.beta[param_j] + dchi2
				for param_k in range(param_j + 1):
					if param_j == param_k:
						A_jk = (1.0 / variance) * self.df[param_j] * self.df[param_k] * (1.0 + self.r)
					else:
						A_jk = (1.0 / variance) * self.df[param_j] * self.df[param_k]
	
					self.A[param_j][param_k] = self.A[param_j][param_k] + A_jk
					self.A[param_k][param_j] = self.A[param_k][param_j] + A_jk


# Useless code!!!
#
#	def chi2_derivatives(self, param):
#		"Get the derivative of the chi2 function at 'param' "
#
#		params_tmp1 = []
#		params_tmp2 = []
#		for i in range(len(self.params)):
#			params_tmp1.append(self.params[i])
#			params_tmp2.append(self.params[i])
#
#		if params_tmp1[param] != 0:
#			delta = abs(params_tmp1[param] / self.large)
#		else:
#			delta = self.tiny
#		params_tmp1[param] = self.params[param] - delta
#		params_tmp2[param] = self.params[param] + 2.0 * delta
#
#		if self.mf.min_debug == 1:
#			print "\nParam: " + `param`
#			print "self.params: " + `self.params`
#			print "params_tmp1: " + `params_tmp1`
#			print "params_tmp2: " + `params_tmp2`
#
#		back_calc_tmp1 = []
#		back_calc_tmp2 = []
#		for i in range(len(self.types)):
#			back_calc_tmp1.append(self.function(self.function_options, self.types[i], params_tmp1))
#			back_calc_tmp2.append(self.function(self.function_options, self.types[i], params_tmp2))
#		y1 = self.chi2_func(self.values, back_calc_tmp1, self.errors)
#		y2 = self.chi2_func(self.values, back_calc_tmp2, self.errors)
#
#		if self.mf.min_debug == 1:
#			print "Vals1: " + `self.values`
#			print "Back calc1: " + `back_calc_tmp1`
#			print "Errors: " + `self.errors`
#			print "Vals2: " + `self.values`
#			print "Back calc2: " + `back_calc_tmp2`
#			print "Errors: " + `self.errors`
#			print "Y1: " + `y1`
#			print "Y2: " + `y2`
#			print "d(chi2): " + `(y2 - y1) / (2.0 * delta)`
#
#		return (y2 - y1) / (2.0 * delta)
#
#
#	def derivative(self, type, param):
#		"Get the derivative of the function at 'param' "
#
#		params_tmp1 = []
#		params_tmp2 = []
#		for i in range(len(self.params)):
#			params_tmp1.append(self.params[i])
#			params_tmp2.append(self.params[i])
#
#		if params_tmp1[param] != 0:
#			delta = abs(params_tmp1[param] / self.large)
#		else:
#			delta = self.tiny
#		params_tmp1[param] = self.params[param] - delta
#		params_tmp2[param] = self.params[param] + 2.0 * delta
#
#		if self.mf.min_debug == 1:
#			print "\nType: " + `type`
#			print "Param: " + `param`
#			print "self.params: " + `self.params`
#			print "params_tmp1: " + `params_tmp1`
#			print "params_tmp2: " + `params_tmp2`
#
#		y1 = self.function(self.function_options, type, params_tmp1)
#		y2 = self.function(self.function_options, type, params_tmp2)
#
#		if self.mf.min_debug == 1:
#			print "Y1: " + `y1`
#			print "Y2: " + `y2`
#			print "df: " + `(y2 - y1) / (2.0 * delta)`
#
#		return (y2 - y1) / (2.0 * delta)


	def linear_solve(self, A, b):
		"""Solves a system of linear equations such that Ax = b, using Gauss-Jordan elimination.

		'A' is a matrix.
		'b' is a vector.
		'x' is the returned solution vector.
		"""

		# Tests for matrix and vector compatibility.
		if len(A) != len(A[0]) or len(A) != len(b):
			print "Matrix or vector not the right dimensions."
			print "Matrix A is: " + `A`
			print "Vector b is: " + `b`
			print "Quitting program."
			sys.exit()

		# Construct the augmented matrix [A|b]
		Ab = []
		for row in range(len(A)):
			Ab.append([])
			for col in range(len(A[row])):
				Ab[row].append(A[row][col])
			Ab[row].append(b[row])
		if self.mf.min_debug == 1:
			print "Ab: " + `Ab`

		# Row reduce [A|b].
		if self.mf.min_debug == 1:
			print "\nReducing A"
		for i in range(len(A)):
			if self.mf.min_debug == 1:
				print "Row: " + `i`
			Ab = self.gauss_jordan_iterate(Ab, i)

		# Now return only the last column of the matrix.
		x = []
		for row in range(len(Ab)):
			x.append(Ab[row][-1])
		if self.mf.min_debug == 1:
			print "Solution is: " + `x`
		return x


	def gauss_jordan_iterate(self, A, i):
		"""Row reduce by Gauss-Jordan elimination.

		'A' is the matrix to row reduce.
		'i' is the index of the row to work with.
		"""

		num_rows = len(A)
		num_cols = len(A[0])

		# If A[i][i] == 0 we cannot divide by it.
		if A[i][i] == 0:
			# Flag for matrix singularity.
			singular_matrix = 0

			# Look for a non-zero entry below this row.
			for j in range(i,num_rows):
				if A[j][i] != 0:
					# Switching rows.
					tmp_row = A[i]
					A[i] = A[j]
					A[j] = tmp_row
					singular_matrix = 1       # Crisis adverted.
					break
			if singular_matrix == 0:
				print "The matrix A " + `A` + " is not singular, quitting program."
				sys.exit()
		if self.mf.min_debug == 1:
			print "\tA pre norm: " + `A`

		# Normalize the row A[i] so that A[i][i] == 1.
		factor = A[i][i]
		for col in range(num_cols):
			A[i][col] = A[i][col] / factor

		if self.mf.min_debug == 1:
			print "\tA norm: " + `A`

		# Now go through all the other rows and do the subtractions.
		for row in range(num_rows):
			# Don't subtract self.
			if row == i:
				continue
			factor = A[row][i]
			for col in range(num_cols):
				A[row][col] = A[row][col] - factor*A[i][col]

		if self.mf.min_debug == 1:
			print "\tA sub: " + `A`

		# We have finished reducing for this pivot.
		return A
