from LinearAlgebra import inverse
from Numeric import copy, matrixmultiply
from re import match

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


def newton(func, dfunc, d2func, x0, line_search_algor='Not set', args=(), tol=1e-5, maxiter=1000, full_output=0, print_flag=1):
	"""Pure Newton minimisation.

	Function options
	~~~~~~~~~~~~~~~~

	func			- The function to minimise.
	dfunc			- The function which returns the gradient vector.
	d2func			- The function which returns the hessian matrix.
	x0			- The initial parameter vector.
	args			- The tuple of arguments to supply to the functions func, dfunc, and d2func.
	tol			- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
	maxiter			- The maximum number of iterations.
	full_output		- A flag specifying what should be returned (see below).
	print_flag		- A flag specifying how much information should be printed to standard output during minimisation:

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

	k	- The iteration number.
	xk	- Parameter vector at iteration number k.
	fk	- Function value at xk.
	fk_last	- Function value at xk-1.
	dfk	- Gradient vector at xk.
	d2fk	- Hessian matrix at xk.
	pk	- Descent direction of the iteration number k.

	"""

	# Initial values before the first iteration.
	xk = x0
	fk = apply(func, (x0,)+args)
	dfk = apply(dfunc, (x0,)+args)
	d2fk = apply(d2func, (x0,)+args)

	# Start the iteration counter.
	k = 0

	# Debugging code.
	if print_flag == 1:
		k2 = 0

	# Iterate until the local minima is found.
	while 1:
		if print_flag == 2:
			print "\n\n<<<Newton iteration k=" + `k` + " >>>"
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

		# Calculate the Newton search direction for iteration k.
		pk = -matrixmultiply(inverse(d2fk), dfk)

		# Backtracking line search.
		if match('^[Bb]ack', line_search_algor):
			alpha = backtrack(func, args, xk, fk, dfk, pk, a_init=1.0)
		# Nocedal and Wright interpolation based line search.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', line_search_algor):
			alpha = nocedal_wright_interpol(func, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, print_flag=0)
		# Nocedal and Wright line search for the Wolfe conditions.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', line_search_algor):
			alpha = nocedal_wright_wolfe(func, dfunc, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, eta=0.9, print_flag=0)
		# More and Thuente line search.
		elif match('^[Mm]ore[ _][Tt]huente$', line_search_algor):
			alpha = more_thuente(func, dfunc, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, eta=0.9, print_flag=0)
		# No line search.
		elif match('^[Nn]one$', line_search_algor):
			alpha = 1.0
		# No match to line search string.
		else:
			raise NameError, "The line search algorithm " + line_search_algor + " is not setup for Newton minimisation.\n"

		# Find the parameter vector, function value, gradient vector, and hessian matrix for iteration k+1.
		xk_new = xk + alpha * pk
		fk_new = apply(func, (xk_new,)+args)
		dfk_new = apply(dfunc, (xk_new,)+args)
		d2fk_new = apply(d2func, (xk_new,)+args)

		# Test for the local minimum.
		if abs(fk - fk_new) <= tol:
			if full_output:
				return xk_new, fk_new, k+1, 0
			else:
				return xk_new

		# Update data for the next iteration.
		k = k + 1
		xk = xk_new
		fk = fk_new
		dfk = copy.deepcopy(dfk_new)
		d2fk = copy.deepcopy(d2fk_new)

		# Debugging code.
		if print_flag == 1:
			k2 = k2 + 1
