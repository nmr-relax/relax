from Numeric import Float64, copy, identity, zeros

def coordinate_descent(func, dfunc, x0, line_search, args=(), tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
	"""Back-and-forth coordinate descent minimisation.

	Function options
	~~~~~~~~~~~~~~~~

	func		- The function to minimise.
	dfunc		- The function which returns the gradient vector.
	x0		- The initial parameter vector.
	line_search	- The line search function.
	args		- The tuple of arguments to supply to the functions func, and dfunc.
	tol		- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
	maxiter		- The maximum number of iterations.
	full_output	- A flag specifying what should be returned (see below).
	print_flag	- A flag specifying how much information should be printed to standard output during minimisation:

	The print flag corresponds to:
		0 - No output.
		1 - Minimal output.
		2 - Full output.


	Returned objects
	~~~~~~~~~~~~~~~~

	If full_output=0, then only the minimised parameter vector is returned.
	If full_output=1, then the minimised parameter vector, function value at the minimum, number of iterations, and a warning flag are returned.
	The warning flag corresponds to:
		0 - Minimisation terminated successfully.
		1 - Maximum number of iterations have been reached.


	Internal variables
	~~~~~~~~~~~~~~~~~~

	k		- The iteration number.
	n		- The coordinate descent iteration number.
	dir		- Matrix containing the coordinate descent directions.
	back		- Flag specifying if the minimiser should move back (1) or forth (0).
	pk		- Descent direction of the iteration number k.
	xk		- Parameter vector at iteration number k.
	fk		- Function value at xk.
	dfk		- Gradient vector at xk.
	xk_new		- Parameter vector at iteration number k+1.
	fk_new		- Function value at xk+1.
	dfk_new		- Gradient vector at xk+1.

	"""

	# Initial values before the first iteration.
	xk = x0
	fk = apply(func, (x0,)+args)
	dfk = apply(dfunc, (x0,)+args)

	# Create the coordinate descent directions, and initialise the coordinate descent iteration number and direction flag.
	dir = identity(len(xk), Float64)
	n = 0
	back = 0

	# Start the iteration counter.
	k = 0

	# Debugging code.
	if print_flag == 1:
		k2 = 0

	# Iterate until the local minima is found.
	while 1:
		# Check if the maximum number of iterations has been reached.
		if k >= maxiter:
			if full_output:
				return xk, fk, k, 1
			else:
				return xk

		# Debugging code.
		if print_flag >= 1:
			if print_flag == 2:
				print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
			else:
				if k2 == 100:
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
					k2 = 0

		# Calculate the back-and-forth coordinate descent search direction for iteration k.
		pk = dir[n]
		print "pk: " + `pk`
		if not back:
			if n < len(xk) - 1:
				n = n + 1
			else:
				back = 1
				n = n - 1
		else:
			if n > 0:
				n = n - 1
			else:
				back = 0
				n = n + 1


		# Find the parameter vector, function value, and gradient vector for iteration k+1.
		xk_new = line_search(func, dfunc, args, xk, fk, dfk, pk)
		fk_new = apply(func, (xk_new,)+args)
		dfk_new = apply(dfunc, (xk_new,)+args)

		# Test for the local minimum.
		if abs(fk - fk_new) <= tol:
			if full_output:
				return xk_new, fk_new, k+1, 0
			else:
				return xk_new

		# Increment the iteration number k and move the k+1 parameter vector, function value, gradient vector, and inverse hessian matrix to the k values.
		k = k + 1
		xk = xk_new
		fk = fk_new
		dfk = copy.deepcopy(dfk_new)

		# Debugging code.
		if print_flag == 1:
			k2 = k2 + 1
