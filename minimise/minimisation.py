import sys
from re import match

#try:
#	from scipy.optimize import fmin, fmin_bfgs, fmin_ncg
#	simplex_scipy = fmin
#	bfgs_scipy = fmin_bfgs
#	ncg_scipy = fmin_ncg
#	noscipy_flag = 0
#except ImportError:
#	print "Scipy is not installed, cannot use simplex, BFGS, or Newton conjugate gradient minimisation from the scipy package."
noscipy_flag = 1

# Grid search.
from minimise.grid import grid

# Line search algorithms.
from minimise.coordinate_descent import coordinate_descent
from minimise.steepest_descent import steepest_descent
from minimise.bfgs import bfgs
from minimise.newton import newton

# Trust region algorithms.
from minimise.cauchy_point import cauchy_point
from minimise.dogleg import dogleg
from minimise.levenberg_marquardt import levenberg_marquardt

# Other algorithms.
from minimise.simplex import simplex


def minimise(func, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
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
	if match('^[Gg]rid', min_algor):
		if print_flag:
			print "\n\n<<< Grid search >>>"
		xk, fk, k = grid(func, args=args, grid_ops=min_options, print_flag=print_flag)
		f_count = k

	# Fixed parameter values.
	elif match('^[Ff]ixed', min_algor):
		if print_flag:
			print "\n\n<<< Fixed initial parameter values >>>"
		xk = min_options
		fk = apply(func, (xk,)+args)
		k, f_count = 1, 1


	# Scipy optimisation methods.
	#############################

	# Simplex minimisation (scipy).
	elif match('^[Ss]implex[ _][Ss]cipy$', min_algor):
		if print_flag:
			print "\n\n<<< Simplex minimisation (scipy) >>>"
		if noscipy_flag:
			print "Simplex minimisation has been choosen yet the scipy python module has not been installed."
			sys.exit()
		results = simplex_scipy(func, x0, args=args, xtol=1e-30, ftol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		xk, fk, k, f_count, warning = results
		warning = `warning`

	# Quasi-Newton BFGS minimisation (scipy).
	elif match('^[Bb][Ff][Gg][Ss][ _][Ss]cipy$', min_algor):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation (scipy) >>>"
		if noscipy_flag:
			print "Quasi-Newton BFGS minimisation from the scipy python module has been choosen yet the module has not been installed."
			sys.exit()
		xk, fk, f_count, g_count, warning = bfgs_scipy(func, x0, fprime=dfunc, args=args, avegtol=func_tol, maxiter=maxiter, full_output=1, disp=print_flag)
		k = f_count
		warning = `warning`


	# Newton Conjugate Gradient minimisation (scipy).
	elif match('^[Nn][Cc][Gg][ _][Ss]cipy$', min_algor):
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
	elif match('^[Cc][Dd]$', min_algor) or match('^[Cc]oordinate[ _-][Dd]escent$', min_algor):
		if print_flag:
			print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
		min = coordinate_descent(func, dfunc=dfunc, args=args, x0=x0, line_search_algor=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', min_algor):
		if print_flag:
			print "\n\n<<< Steepest descent minimisation >>>"
		min = steepest_descent(func, dfunc=dfunc, args=args, x0=x0, line_search_algor=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', min_algor):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
		min = bfgs(func, dfunc=dfunc, args=args, x0=x0, line_search_algor=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()

	# Newton minimisation.
	elif match('^[Nn]ewton$', min_algor):
		if print_flag:
			print "\n\n<<< Newton minimisation >>>"
		min = newton(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, line_search_algor=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()


	# Trust-region algorithms.
	##########################

	# Cauchy point minimisation.
	elif match('^[Cc]auchy', min_algor):
		if print_flag:
			print "\n\n<<< Cauchy point minimisation >>>"
		min = cauchy_point(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()

	# Dogleg minimisation.
	elif match('^[Dd]ogleg', min_algor):
		if print_flag:
			print "\n\n<<< Dogleg minimisation >>>"
		min = dogleg(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, hessian_type=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
		if print_flag:
			print "\n\n<<< Levenberg-Marquardt minimisation >>>"
		min = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()


	# Other algorithms.
	###################

	# Simplex minimisation.
	elif match('^[Ss]implex$', min_algor):
		if print_flag:
			print "\n\n<<< Simplex minimisation >>>"
		min = simplex(func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = min.minimise()
		else:
			xk = min.minimise()


	# No match to minimiser string.
	###############################

	else:
		print "Minimiser type set incorrectly.  The minimiser " + min_algor + " is not programmed.\n"
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
