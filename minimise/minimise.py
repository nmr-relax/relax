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
	print "Python module scipy not installed, cannot use simplex, BFGS, or Newton conjugate gradient minimisation."
	noscipy_flag = 1

# Grid search.
from grid import grid

# Generic minimisation classes.
from generic_line_search import generic_line_search
#from generic_trust_region import generic_trust_region
#from generic_conjugate_grad import generic_conjugate_grad

# Line search minimisers.
import coordinate_descent
import steepest_descent
import bfgs
import newton

# Trust region minimisers.
#from cauchy_point import cauchy_point
from levenberg_marquardt import levenberg_marquardt


def minimise(func, x0=None, dfunc=None, d2func=None, args=(), minimiser=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
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

	# Initialisation.
	iter = 0
	fc = 0
	gc = 0
	hc = 0
	type_line_search = 0
	type_trust_region = 0
	type_conjugate_grad = 0
	backup_current_data = 0
	refresh_d2f_args = None


	# Parameter initialisation methods.
	###################################

	# Grid search.
	if match('^[Gg]rid', minimiser[0]):
		if print_flag:
			print "\n\n<<< Grid search >>>"
		x0, f0, iter = grid(func, args=args, grid_ops=minimiser[1], print_flag=print_flag)
		if print_flag:
			data_printout(iter, x0, f0, iter, 0, 0, 0)
		if full_output:
			return x0, f0, iter, iter, 0, 0, 0
		else:
			return x0

	# Fixed parameter values.
	elif match('^[Ff]ixed', minimiser[0]):
		if print_flag:
			print "\n\n<<< Fixed initial parameter values >>>"
		x0 = minimiser[1]
		f0 = apply(func, (x0,)+args)
		if print_flag:
			data_printout(1, x0, f0, 1, 0, 0, 0)
		if full_output:
			return x0, f0, 1, 0, 0, 0
		else:
			return x0


	# Scipy optimisation methods.
	#############################

	# Simplex minimisation (scipy).
	elif match('^[Ss]implex[ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Simplex minimisation (scipy) >>>"
		if noscipy_flag:
			print "Simplex minimisation has been choosen yet the scipy python module has not been installed."
			sys.exit()
		xk, fk, iter, fc, warn_flag = simplex_scipy(func, x0, args=args, xtol=1e-30, ftol=func_tol, maxiter=maxiter, full_output=full_output, disp=print_flag)
		if print_flag:
			data_printout(iter, xk, fk, fc, 0, 0, warn_flag)
		if full_output:
			return xk, fk, iter, fc, 0, 0, warn_flag
		else:
			return xk

	# Quasi-Newton BFGS minimisation (scipy).
	elif match('^[Bb][Ff][Gg][Ss][ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation (scipy) >>>"
		if noscipy_flag:
			print "Quasi-Newton BFGS minimisation from the scipy python module has been choosen yet the module has not been installed."
			sys.exit()
		xk, fk, fc, gc, warn_flag = bfgs_scipy(func, x0, fprime=dfunc, args=args, avegtol=func_tol, maxiter=maxiter, full_output=full_output, disp=print_flag)
		if print_flag:
			data_printout(fc, xk, fk, fc, gc, 0, warn_flag)
		if full_output:
			return xk, fk, fc, fc, gc, 0, warn_flag
		else:
			return xk

	# Newton Conjugate Gradient minimisation (scipy).
	elif match('^[Nn][Cc][Gg][ _][Ss]cipy$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Newton Conjugate Gradient minimisation (scipy) >>>"
		if noscipy_flag:
			print "Newton Conjugate Gradient minimisation has been choosen yet the scipy python module has not been installed."
			sys.exit()
		xk, fk, fc, gc, hc, warn_flag = ncg_scipy(func, x0, fprime=dfunc, fhess=d2func, args=args, avextol=func_tol, maxiter=maxiter, full_output=full_output, disp=print_flag)
		if print_flag:
			data_printout(fc, xk, fk, fc, gc, hc, warn_flag)
		if full_output:
			return xk, fk, fc, fc, gc, hc, warn_flag
		else:
			return xk


	# Optimisation methods (all specific code).
	###########################################

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', minimiser[0]) or match('^[Ll]evenburg-[Mm]arquardt$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Levenberg-Marquardt minimisation >>>"
		xk, fk, iter, warn_flag = levenberg_marquardt(func, dfunc, minimiser[1], x0, errors, args=args, tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)
		if print_flag:
			data_printout(iter, xk, fk, iter, 0, 0, warn_flag)
		if full_output:
			return xk, fk, iter, fc, 0, 0, warn_flag
		else:
			return xk


	# Optimisation methods (use general code).
	##########################################

	# Back-and-forth coordinate descent minimisation.
	elif match('^[Cc][Dd]$', minimiser[0]) or match('^[Cc]oordinate-[Dd]escent$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
		type_line_search = 1
		class_function = generic_line_search
		init_data = coordinate_descent.init_data

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', minimiser[0]) or match('^[Ss]teepest[ _][Dd]escent$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Steepest descent minimisation >>>"
		type_line_search = 1
		class_function = generic_line_search
		init_data = steepest_descent.init_data

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
		type_line_search = 1
		class_function = generic_line_search
		class_function_args = (bfgs.dir,)
		backup_current_data = 1
		init_data = bfgs.init_data
		d2func = bfgs.matrix_update
		refresh_d2f_args = bfgs.refresh_d2f_args

	# Newton minimisation.
	elif match('^[Nn]ewton$', minimiser[0]):
		if print_flag:
			print "\n\n<<< Newton minimisation >>>"
		type_line_search = 1
		class_function = generic_line_search
		class_function_args = (newton.dir,)
		init_data = newton.init_data


	# No match to minimiser string.
	###############################

	else:
		print "Minimiser type set incorrectly.  The minimiser " + minimiser[0] + " is not programmed.\n"
		sys.exit()



	# Generic minimisation code.
	############################

	# Initial values before the first iteration.
	xk = x0
	fk, dfk, d2fk = init_data(func, dfunc, d2func, args, x0)
	f_args, df_args, d2f_args = args, args, args
	if type_line_search:
		a0 = 1.0

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

		# Make a backup of the current data.
		fk_last = fk
		if backup_current_data:
			xk_last = xk
			if dfunc:
				dfk_last = copy.deepcopy(dfk)
			if d2func:
				d2fk_last = copy.deepcopy(d2fk)

		# Find the new parameter vector xk.
		xk = apply(class_function, (func, dfunc, d2func, args, xk, fk, dfk, d2fk, minimiser, print_flag)+class_function_args)

		# Find the parameter vector, function value, gradient vector, and hessian matrix for iteration k+1.
		fk = apply(func, (xk,)+f_args)
		if dfunc:
			dfk = apply(dfunc, (xk,)+df_args)
		if d2func:
			if refresh_d2f_args:
				d2f_args = refresh_d2f_args(xk_last, xk, fk_last, fk, dfk_last, dfk, d2fk_last)
			d2fk = apply(d2func, (xk,)+d2f_args)

		# Test for the local minimum or if the maximum number of iterations has been reached.
		if abs(fk_last - fk) <= func_tol or  k >= maxiter:
			########## Fix this code.
			if print_flag:
				data_printout(k, xk, fk, k, 0, 0, 0)
			return xk, fk, k, 0, 0, 0, 0

		# Update data for the next iteration.
		k = k + 1

		# Debugging code.
		if print_flag == 1:
			k2 = k2 + 1


def data_printout(iter, x, f, fc, gc, hc, warn):
	print "\nIterations:       " + `iter`
	print "Parameter values: " + `x`
	print "Function value:   " + `f`
	print "Function calls:   " + `fc`
	print "Gradient calls:   " + `gc`
	print "Hessian calls:    " + `hc`
	print "Warning flag:     " + `warn`
