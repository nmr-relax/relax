import sys
from Numeric import copy
from re import match

try:
	from scipy.optimize import fmin, fmin_bfgs, fmin_ncg
	simplex_scipy = fmin
	bfgs_scipy = fmin_bfgs
	ncg_scipy = fmin_ncg
	noscipy_flag = 0
except ImportError:
	print "Scipy is not installed, cannot use simplex, BFGS, or Newton conjugate gradient minimisation from the scipy package."
	noscipy_flag = 1

# Grid search.
from grid import grid

# Generic minimisation classes.
from generic_trust_region import generic_trust_region
#from generic_conjugate_grad import generic_conjugate_grad

# Line search algorithms.
from coordinate_descent import coordinate_descent
from steepest_descent import steepest_descent
from bfgs import bfgs
from newton import newton

# Trust region algorithms.
from levenberg_marquardt import levenberg_marquardt
#from cauchy_point import cauchy_point

# Other algorithms.
from simplex import simplex


def minimise(func, dfunc=None, d2func=None, args=(), x0=None, minimiser=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
	"""Generic code for iterative minimisers.


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

	func_tol		- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
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

	f_count = 0
	g_count = 0
	h_count = 0
	warning = None


	# Parameter initialisation methods.
	###################################

	# Grid search.
	if match('^[Gg]rid', minimiser[0]):
		if print_flag:
			print "\n\n<<< Grid search >>>"
		results = grid(func, args=args, grid_ops=minimiser[1], print_flag=print_flag)
		xk, fk, k = results
		f_count = k

	# Fixed parameter values.
	elif match('^[Ff]ixed', minimiser[0]):
		if print_flag:
			print "\n\n<<< Fixed initial parameter values >>>"
		xk = minimiser[1]
		fk = apply(func, (xk,)+args)
		k, f_count = 1, 1


	# Scipy optimisation methods.
	#############################

	# Simplex minimisation (scipy).
	elif match('^[Ss]implex[ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Simplex minimisation (scipy) >>>"
		if noscipy_flag:
			print "Simplex minimisation has been choosen yet the scipy python module has not been installed."
			sys.exit()
		results = simplex_scipy(func, x0, args=args, xtol=1e-30, ftol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		xk, fk, k, f_count, warning = results
		warning = `warning`

	# Quasi-Newton BFGS minimisation (scipy).
	elif match('^[Bb][Ff][Gg][Ss][ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation (scipy) >>>"
		if noscipy_flag:
			print "Quasi-Newton BFGS minimisation from the scipy python module has been choosen yet the module has not been installed."
			sys.exit()
		xk, fk, f_count, g_count, warning = bfgs_scipy(func, x0, fprime=dfunc, args=args, avegtol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		k = f_count
		warning = `warning`


	# Newton Conjugate Gradient minimisation (scipy).
	elif match('^[Nn][Cc][Gg][ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Newton Conjugate Gradient minimisation (scipy) >>>"
		if noscipy_flag:
			print "Newton Conjugate Gradient minimisation has been choosen yet the scipy python module has not been installed."
			sys.exit()
		xk, fk, f_count, g_count, h_count, warning = ncg_scipy(func, x0, fprime=dfunc, fhess=d2func, args=args, avextol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		k = f_count
		warning = `warning`


	# Line search algorithms.
	#########################

	# Back-and-forth coordinate descent minimisation.
	elif match('^[Cc][Dd]$', minimiser[0]) or match('^[Cc]oordinate-[Dd]escent$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
		min = coordinate_descent()
		results = min.minimise(func, dfunc, d2func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', minimiser[0]) or match('^[Ss]teepest[ _][Dd]escent$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Steepest descent minimisation >>>"
		min = steepest_descent()
		results = min.minimise(func, dfunc, d2func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
		min = bfgs()
		results = min.minimise(func, dfunc, d2func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results

	# Newton minimisation.
	elif match('^[Nn]ewton$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Newton minimisation >>>"
		min = newton()
		results = min.minimise(func, dfunc, d2func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results


	# Trust-region algorithms.
	##########################

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', minimiser[0]) or match('^[Ll]evenburg-[Mm]arquardt$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Levenberg-Marquardt minimisation >>>"
		min = levenberg_marquardt()
		results = min.minimise(func, dfunc, minimiser[1], minimiser[2], x0, args=args, func_tol=func_tol, maxiter=maxiter, full_output=1, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results


	# Other algorithms.
	###################

	# Simplex minimisation.
	elif match('^[Ss]implex$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Simplex minimisation >>>"
		min = simplex()
		results = min.minimise(func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag)
		#results = simplex_scipy(func, x0, args=args, xtol=1e-30, ftol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
		else:
			xk = results


	# No match to minimiser string.
	###############################

	else:
		print "Minimiser type set incorrectly.  The minimiser " + minimiser[0] + " is not programmed.\n"
		sys.exit()


	# Finish.
	if print_flag:
		print "\nIterations:       " + `k`
		print "Parameter values: " + `xk`
		print "Function value:   " + `fk`
		print "Function calls:   " + `f_count`
		print "Gradient calls:   " + `g_count`
		print "Hessian calls:    " + `h_count`
		if warning:
			print "Warning:          " + warning
		else:
			print "Warning:          None"
	if full_output:
		return xk, fk, k, f_count, g_count, h_count, warning
	else:
		return xk
