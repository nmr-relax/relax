import sys
from LinearAlgebra import solve_linear_equations
from Numeric import copy, Float64, concatenate, zeros
from re import match

def levenberg_marquardt(chi2_func, dchi2_func, dfunc, params, errors, args=(), tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
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

	warning_flag = 0

	# Initial value of lambda (the Levenberg-Marquardt fudge factor).
	l = 1.0

	# Get some data structures.
	chi2 = apply(chi2_func, (params,)+args)
	dchi2 = -0.5 * apply(dchi2_func, (params,)+args)
	df = dfunc()

	minimise_num = 1

	# Print the status of the minimiser.
	if print_flag >= 1:
		print "%-4s%-6i%-8s%-46s%-6s%-25e%-8s%-6e" % ("run", 0, "Params:", `params`, "Chi2:", chi2, "l:", l)
	
	# Print the status of the minimiser.
	if print_flag >= 1:
		print_num = 0

	# Iterate until the minimiser is finished.
	while 1:
		# Create the Levenberg-Marquardt matrix.
		lm_matrix = create_lm_matrix(len(params), errors, df, l)

		# Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
		param_change = solve_linear_equations(lm_matrix, dchi2)

		# Add the current parameter vector to the parameter change vector to find the new parameter vector.
		new_params = zeros((len(params)), Float64)
		new_params = params + param_change

		# Recalculate the chi2 statistic.
		chi2_new = apply(chi2_func, (new_params,)+args)
		dchi2 = -0.5 * apply(dchi2_func, (params,)+args)
		df = dfunc()

		# Print debugging info
		if print_flag >= 2:
			print "\n\n"
			print "%-29s%-40s" % ("Minimisation run number:", `minimise_num`)
			for i in range(len(errors)):
				print "%-29s%-40s" % ("Derivative array " + `i` + " is: ", `df[:,i]`)

			print "%-29s%-40s" % ("Levenberg-Marquardt matrix:", `lm_matrix`)
			print "%-29s%-40s" % ("Chi2 grad vector:", `dchi2`)
			print "%-29s%-40s" % ("Old parameter vector:", `params`)
			print "%-29s%-40s" % ("Parameter change vector:", `param_change`)
			print "%-29s%-40s" % ("New parameter vector:", `new_params`)
			print "%-29s%-40e" % ("Chi-squared:", chi2)
			print "%-29s%-40e" % ("Chi-squared new:", chi2_new)
			print "%-29s%-40e" % ("Chi-squared diff:", chi2 - chi2_new)
			print "%-29s%-40e" % ("l:", l)


		# Test improvement.
		if chi2_new > chi2:
			if l <= 1e99:
				l = l * 10.0
		else:
			# Finish minimising when the chi-squared difference is insignificant.
			if chi2 - chi2_new < tol:
				if print_flag >= 2:
					print "\n%-29s%-40e" % ("Chi-squared diff:", chi2 - chi2_new)
					print "%-29s%-40e" % ("Chi-squared diff limit:", 1e-10)
					print "Insignificant chi2 difference, stopped minimising."
				break
			if l >= 1e-99:
				l = l / 10.0

			# Update function parameters and chi-squared value.
			params = copy.deepcopy(new_params)
			chi2 = chi2_new

		# Print the status of the minimiser.
		if print_flag >= 1:
			print_num = print_num + 1
			if print_num == 1000:
				print "%-4s%-6i%-8s%-46s%-6s%-25s%-8s%-6s" % ("run", minimise_num, "Params:", `new_params`, "Chi2:", `chi2_new`, "l:", `l`)
				print_num = 0
		
		# Check to see if the maximum number of iterations have been reached.
		if minimise_num >= maxiter:
			warning_flag = 1
			break

		minimise_num = minimise_num + 1

	if full_output:
		return (params, chi2, minimise_num, warning_flag)
	else:
		return (params, chi2)


def create_lm_matrix(n, errors, df, l):
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
	matrix = zeros((n, n), Float64)

	# Loop over the error points from i=1 to n.
	for i in range(len(errors)):
		# Calculate the inverse of the variance to minimise calculations.
		i_variance = 1.0 / errors[i]**2

		# Loop over all function parameters.
		for param_j in range(n):
			# Loop over the function parameters from the first to 'param_j' to create the Levenberg-Marquardt matrix.
			for param_k in range(param_j + 1):
				if param_j == param_k:
					matrix_jk = i_variance * df[param_j, i] * df[param_k, i] * (1.0 + l)
				else:
					matrix_jk = i_variance * df[param_j, i] * df[param_k, i]

				matrix[param_j, param_k] = matrix[param_j, param_k] + matrix_jk
				matrix[param_k, param_j] = matrix[param_k, param_j] + matrix_jk
	return matrix
