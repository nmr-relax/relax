from Numeric import copy

def generic_minimise(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, xk_new, fk_new, dfk_new, d2fk_new, min_func, min_func_args, tol, maxiter, print_flag):
	"""Generic code for iterative minimisers.

	The function min_func should return the parameter array, xk_new, for the next iteration, and is the code specific to the minimisation algorithm.


	Function options
	~~~~~~~~~~~~~~~~

	func			- The function to minimise.
	dfunc			- The function which returns the gradient vector.
	d2func			- The function which returns the hessian matrix or approximation.

	f_args			- The tuple of arguments to supply to the function func.
	df_args			- The tuple of arguments to supply to the function dfunc.
	d2f_args		- The tuple of arguments to supply to the function d2func.

	xk			- The parameter vector which on input is the initial values, x0.
	fk			- The function value which on input corresponds to x0.
	dfk			- The gradient vector which on input corresponds to x0.
	d2fk			- The hessian matrix or approximation which on input corresponds to x0.

	xk_new			- The parameter vector for the next iteration which on input can be anything.
	fk_new			- The function value for the next iteration which on input can be anything.
	dfk_new			- The gradient vector for the next iteration which on input can be anything.
	d2fk_new		- The hessian matrix for the next iteration which on input can be anything.

	tol			- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
	maxiter			- The maximum number of iterations.
	print_flag		- A flag specifying how much information should be printed to standard output during minimisation:

	The print flag corresponds to:
		0 - No output.
		1 - Minimal output.
		2 - Full output.


	Returned objects
	~~~~~~~~~~~~~~~~

	The minimised parameter vector, function value at the minimum, number of iterations, and a warning flag are returned.
	The warning flag corresponds to:
		0 - Minimisation terminated successfully.
		1 - Maximum number of iterations have been reached.
	"""

	# Start the iteration counter.
	k = 0

	# Debugging code.
	if print_flag == 1:
		k2 = 0

	# Iterate until the local minima is found.
	while 1:
		if print_flag == 2:
			print "\n\n<<<Main iteration k=" + `k` + " >>>"

		# Debugging code.
		if print_flag >= 1:
			if print_flag == 2:
				print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
			else:
				if k2 == 100:
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
					k2 = 0

		# Find the new parameter vector xk_new.
		xk_new = apply(min_func, (func, dfunc, d2func, f_args, xk, fk, dfk, d2fk,)+min_func_args)

		# Find the parameter vector, function value, gradient vector, and hessian matrix for iteration k+1.
		fk_new = apply(func, (xk_new,)+f_args)
		if dfunc:
			dfk_new = apply(dfunc, (xk_new,)+df_args)
		if d2func:
			d2fk_new = apply(d2func, (xk_new,)+d2f_args)

		# Test for the local minimum or if the maximum number of iterations has been reached.
		if abs(fk - fk_new) <= tol or  k+1 >= maxiter:
			return xk_new, fk_new, k+1, 0

		# Update data for the next iteration.
		k = k + 1
		xk = xk_new
		fk = fk_new
		if dfunc:
			dfk = copy.deepcopy(dfk_new)
		if d2func:
			d2fk = copy.deepcopy(d2fk_new)

		# Debugging code.
		if print_flag == 1:
			k2 = k2 + 1
