from Numeric import Float64, zeros
from copy import deepcopy
from re import match

from generic_minimise import generic_minimise
import bfgs
import newton

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


def generic_line_search(func, dfunc, d2func, x0, minimiser=None, line_search_algor=None, args=(), tol=1e-5, maxiter=1000, full_output=0, print_flag=1):
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

	# Setup the min_func arguments.
	min_func_args = (minimiser, line_search_algor,)

	# Initialisation code.
	xk = x0
	fk = 0.0
	dfk = zeros((len(xk)), Float64)
	d2fk = zeros((len(xk), len(xk)), Float64)

	xk_new = zeros((len(xk)), Float64)
	fk_new = 0.0
	dfk_new = zeros((len(xk)), Float64)
	d2fk_new = zeros((len(xk), len(xk)), Float64)

	f_args = deepcopy(args)
	df_args = deepcopy(args)
	d2f_args = deepcopy(args)

	print "xk: " + `xk`
	print "fk: " + `fk`
	print "dfk: " + `dfk`
	print "d2fk: " + `d2fk`
	print "xk_new: " + `xk_new`
	print "fk_new: " + `fk_new`
	print "dfk_new: " + `dfk_new`
	print "d2fk_new: " + `d2fk_new`

	if match('^[Bb][Ff][Gg][Ss]$', minimiser):
		bfgs.setup(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, xk_new, fk_new, dfk_new, d2fk_new, args, print_flag)
	elif match('^[Nn]ewton$', minimiser):
		newton.setup(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, args, print_flag)

	print "xk: " + `xk`
	print "fk: " + `fk`
	print "dfk: " + `dfk`
	print "d2fk: " + `d2fk`
	print "xk_new: " + `xk_new`
	print "fk_new: " + `fk_new`
	print "dfk_new: " + `dfk_new`
	print "d2fk_new: " + `d2fk_new`

	# Main part of the minimisation.
	output = generic_minimise(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, xk_new, fk_new, dfk_new, d2fk_new, min_func, min_func_args, tol, maxiter, print_flag)
	xk_fin, fk_fin, k, warn_flag = output

	# Return the final values.
	if full_output:
		return xk_fin, fk_fin, k, warn_flag
	else:
		return xk_fin


def min_func(func, dfunc, d2func, args, xk, fk, dfk, d2fk, minimiser, line_search_algor):

	# Calculate the search direction for iteration k.
	if match('^[Bb][Ff][Gg][Ss]$', minimiser):
		pk = bfgs.dir(dfk, d2fk)
	elif match('^[Nn]ewton$', minimiser):
		pk = newton.dir(dfk, d2fk)

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

	# Find the new parameter vector.
	xk_new = xk + alpha * pk
	return xk_new
