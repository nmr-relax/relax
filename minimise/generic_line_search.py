from Numeric import Float64, zeros
from copy import deepcopy
from re import match

import bfgs
import newton

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


def generic_line_search(func, dfunc, d2func, args, xk, fk, dfk, d2fk, minimiser, print_flag, dir):
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

	# Calculate the search direction for iteration k.
	pk = dir(dfk, d2fk)

	# Backtracking line search.
	if match('^[Bb]ack', minimiser[1]):
		alpha = backtrack(func, args, xk, fk, dfk, pk, a_init=1.0)
	# Nocedal and Wright interpolation based line search.
	elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', minimiser[1]):
		alpha = nocedal_wright_interpol(func, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, print_flag=0)
	# Nocedal and Wright line search for the Wolfe conditions.
	elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', minimiser[1]):
		alpha = nocedal_wright_wolfe(func, dfunc, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, eta=0.9, print_flag=0)
	# More and Thuente line search.
	elif match('^[Mm]ore[ _][Tt]huente$', minimiser[1]):
		alpha = more_thuente(func, dfunc, args, xk, fk, dfk, pk, a_init=1.0, mu=0.0001, eta=0.9, print_flag=0)
	# No line search.
	elif match('^[Nn]one$', minimiser[1]):
		alpha = 1.0
	# No match to line search string.
	else:
		raise NameError, "The line search algorithm " + minimiser[1] + " is not setup for Newton minimisation.\n"

	# Find the new parameter vector.
	xk_new = xk + alpha * pk
	return xk_new
