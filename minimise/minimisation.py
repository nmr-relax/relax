from re import match

# Grid search.
from minimise.grid import grid

# Line search algorithms.
from minimise.coordinate_descent import coordinate_descent
from minimise.steepest_descent import steepest_descent
from minimise.bfgs import bfgs
from minimise.newton import newton
from minimise.newton_cg import newton_cg

# Trust region algorithms.
from minimise.cauchy_point import cauchy_point
from minimise.dogleg import dogleg
from minimise.steihaug_cg import steihaug
from minimise.exact_trust_region import exact_trust_region

# Conjugate gradient algorithms.
from minimise.fletcher_reeves_cg import fletcher_reeves
from minimise.polak_ribiere_cg import polak_ribiere
from minimise.polak_ribiere_plus_cg import polak_ribiere_plus
from minimise.hestenes_stiefel_cg import hestenes_stiefel

# Other algorithms.
from minimise.levenberg_marquardt import levenberg_marquardt
from minimise.simplex import simplex


def minimise(func, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
	"""Generic code for iterative minimisers.


	Function options
	~~~~~~~~~~~~~~~~

	func - The function to minimise.
	dfunc - The function which returns the gradient vector.
	d2func - The function which returns the Hessian matrix or approximation.

	args - The tuple of arguments to supply to the functions func, dfunc, and d2func.

	xk - The parameter vector which on input is the initial values, x0.
	fk - The function value which on input corresponds to x0.
	dfk - The gradient vector which on input corresponds to x0.
	d2fk - The Hessian matrix or approximation which on input corresponds to x0.

	xk_new - The parameter vector for the next iteration which on input can be anything.
	fk_new - The function value for the next iteration which on input can be anything.
	dfk_new - The gradient vector for the next iteration which on input can be anything.
	d2fk_new - The Hessian matrix for the next iteration which on input can be anything.

	func_tol - The cutoff value used to terminate minimisation by comparison to the difference
		in function values between iterations.
	maxiter - The maximum number of iterations.
	print_flag - A flag specifying how much information should be printed to standard output
		during minimisation.  The print flag corresponds to:
			0 - No output.
			1 - Minimal output.
			2 - Full output.
	"""

	# Parameter initialisation methods.
	###################################

	# Grid search.
	if match('^[Gg]rid', min_algor):
		if print_flag:
			print "\n\n<<< Grid search >>>"
		xk, fk, k = grid(func, args=args, grid_ops=min_options, print_flag=print_flag)
		if full_output:
			results = (xk, fk, k, k, 0, 0, None)
		else:
			results = xk

	# Fixed parameter values.
	elif match('^[Ff]ixed', min_algor):
		if print_flag:
			print "\n\n<<< Fixed initial parameter values >>>"
		xk = min_options
		fk = apply(func, (xk,)+args)
		if full_output:
			results = (xk, fk, 1, 1, 0, 0, None)
		else:
			results = xk


	# Line search algorithms.
	#########################

	# Back-and-forth coordinate descent minimisation.
	elif match('^[Cc][Dd]$', min_algor) or match('^[Cc]oordinate[ _-][Dd]escent$', min_algor):
		if print_flag:
			print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
		results = coordinate_descent(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', min_algor):
		if print_flag:
			print "\n\n<<< Steepest descent minimisation >>>"
		results = steepest_descent(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', min_algor):
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
		results = bfgs(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Newton minimisation.
	elif match('^[Nn]ewton$', min_algor):
		if print_flag:
			print "\n\n<<< Newton minimisation >>>"
		results = newton(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Newton-CG minimisation.
	elif match('^[Nn]ewton[ _-][Cc][Gg]$', min_algor) or match('^[Nn][Cc][Gg]$', min_algor):
		if print_flag:
			print "\n\n<<< Newton Conjugate Gradient minimisation >>>"
		results = newton_cg(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Trust-region algorithms.
	##########################

	# Cauchy point minimisation.
	elif match('^[Cc]auchy', min_algor):
		if print_flag:
			print "\n\n<<< Cauchy point minimisation >>>"
		results = cauchy_point(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Dogleg minimisation.
	elif match('^[Dd]ogleg', min_algor):
		if print_flag:
			print "\n\n<<< Dogleg minimisation >>>"
		results = dogleg(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# CG-Steihaug minimisation.
	elif match('^[Cc][Gg][-_ ][Ss]teihaug', min_algor) or match('^[Ss]teihaug', min_algor):
		if print_flag:
			print "\n\n<<< CG-Steihaug minimisation >>>"
		results = steihaug(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Exact trust region minimisation.
	elif match('^[Ee]xact', min_algor):
		if print_flag:
			print "\n\n<<< Exact trust region minimisation >>>"
		results = exact_trust_region(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Conjugate gradient algorithms.
	################################

	# Fletcher-Reeves conjugate gradient minimisation.
	elif match('^[Ff][Rr]$', min_algor) or match('^[Ff]letcher[-_ ][Rr]eeves$', min_algor):
		if print_flag:
			print "\n\n<<< Fletcher-Reeves conjugate gradient minimisation >>>"
		results = fletcher_reeves(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Polak-Ribière conjugate gradient minimisation.
	elif match('^[Pp][Rr]$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere$', min_algor):
		if print_flag:
			print "\n\n<<< Polak-Ribière conjugate gradient minimisation >>>"
		results = polak_ribiere(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Polak-Ribière + conjugate gradient minimisation.
	elif match('^[Pp][Rr]\+$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere\+$', min_algor):
		if print_flag:
			print "\n\n<<< Polak-Ribière + conjugate gradient minimisation >>>"
		results = polak_ribiere_plus(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Hestenes-Stiefel conjugate gradient minimisation.
	elif match('^[Hh][Ss]$', min_algor) or match('^[Hh]estenes[-_ ][Ss]tiefel$', min_algor):
		if print_flag:
			print "\n\n<<< Hestenes-Stiefel conjugate gradient minimisation >>>"
		results = hestenes_stiefel(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Other algorithms.
	###################

	# Simplex minimisation.
	elif match('^[Ss]implex$', min_algor):
		if print_flag:
			print "\n\n<<< Simplex minimisation >>>"
		results = simplex(func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
		if print_flag:
			print "\n\n<<< Levenberg-Marquardt minimisation >>>"
		results = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# No match to minimiser string.
	###############################

	else:
		print "Minimiser type set incorrectly.  The minimiser " + min_algor + " is not programmed.\n"
		return


	# Finish.
	if print_flag:
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
			print "\nParameter values: " + `xk`
			print "Function value:   " + `fk`
			print "Iterations:       " + `k`
			print "Function calls:   " + `f_count`
			print "Gradient calls:   " + `g_count`
			print "Hessian calls:    " + `h_count`
			if warning:
				print "Warning:          " + warning
			else:
				print "Warning:          None"
		else:
			print "\nParameter values: " + `results`

	return results
