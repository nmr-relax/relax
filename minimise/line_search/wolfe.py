from Numeric import copy, dot, sqrt

def wolfe(func, dfunc, args, xk, fk, dfk, pk, a1=1.0, a_max=1e4, c1=1e-4, c2=0.9, print_flag=1):
	"""A line search algorithm implemented using the strong Wolfe condittions.

	Algorithm 3.2, page 59, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	Requires the gradient function.

	The one dimensional function to minimise on is denoted phi(ai) and is given by the formula:
		phi(ai) = func(xk + ai.pk)
	The gradient of the function phi(ai) is given by the dot product:
		dphi(ai) = dfunc(xk + ai.pk).pk


	Function options
	~~~~~~~~~~~~~~~~

	func		- The function to minimise.
	dfunc		- The function which returns the gradient vector.
	args		- The tuple of arguments to supply to the functions func and dfunc.
	xk		- The parameter vector at minimisation step k.
	fk		- The function value at the point xk.
	dfk		- The function gradient vector at the point xk.
	pk		- The descent direction.
	a1		- Initial step length.
	a_max		- The maximum value for the step length.
	c1		- Constant determining the slope for the sufficient decrease condition (0 < c1 < c2 < 1).
	c2		- Constant used for the Wolfe curvature condition (0 < c1 < c2 < 1).


	Returned objects
	~~~~~~~~~~~~~~~~

	The parameter vector, minimised along the direction xk + ak.pk, to be used at k+1.


	Internal variables
	~~~~~~~~~~~~~~~~~~

	ai		- The step length at line search iteration i.
	xai		- The parameter vector at step length ai.
	phi_ai		- The one dimensional function value at step length ai.
	dfai		- The gradient vector at step length ai given by dfunc(xk + ai.pk).
	dphi_ai		- The one dimensional gradient at step length ai given by dfunc(xk + ai.pk).pk.

	ai_last		- The step length at line search iteration i-1.
	xai_last	- The parameter vector at step length ai-1.
	phi_ai_last	- The one dimensional function value at step length ai-1.
	dfai_last	- The gradient vector at step length ai-1 given by dfunc(xk + ai-1.pk).
	dphi_ai_last	- The one dimensional gradient at step length ai-1 given by dfunc(xk + ai-1.pk).pk.

	"""

	# Initialise values.
	ai = a1
	phi0 = fk
	dphi0 = dot(dfk, pk)
	ai_last = 0.0
	xai_last = copy.deepcopy(xk)
	phi_ai_last = fk
	dfai_last = copy.deepcopy(dfk)
	dphi_ai_last = dot(dfk, pk)
	i = 1

	if print_flag == 1:
		print "\n<Inside line search>"
		print "a1:                       " + `ai`
		print "fk:                       " + `fk`
		print "phi0 = fk:                " + `phi0`
		print "dfk:                      " + `dfk`
		print "pk:                       " + `pk`
		print "dphi0 = dot(dfk, pk):     " + `dphi0`
		print "xk:                       " + `xk`
		print "a0:                       " + `ai_last`
		print "xa0:                      " + `xai_last`
		print "phi_a0:                   " + `phi_ai_last`
		print "dfa0:                     " + `dfai_last`
		print "dphi_a0:                  " + `dphi_ai_last`
		print "c1:                       " + `c1`
		print "c2:                       " + `c2`

	while 1:
		if print_flag == 1:
			print "\t<Line search iteration i=" + `i` + " >"

		# Determine the one dimensional function and gradient values at step length ai.
		xai = xk + ai*pk
		phi_ai = apply(func, (xai,)+args)
		dfai = apply(dfunc, (xai,)+args)
		dphi_ai = dot(dfai, pk)

		if print_flag == 1:
			print "\tai:       " + `ai`
			print "\tai_last:  " + `ai_last`
			print "\tphi_ai:   " + `phi_ai`
			print "\tdfai:     " + `dfai`
			print "\tdphi_ai:  " + `dphi_ai`
			print "\txai:      " + `xai`

		# Check if the sufficient decrease condition is violated.
		# If so, the interval (ai-1, ai) will contain step lengths satisfying the strong Wolfe conditions.
		if not phi_ai <= phi0 + c1*ai*dphi0:
			if print_flag == 1:
				print "\tSufficient decrease condition is violated - zooming"
				print "\tphi_ai not <= phi0 + c1*ai*dphi0"
				print "\tc1*ai*dphi0: " + `c1*ai*dphi0`
				print "\t" + `phi_ai` + " not <= " + `phi0 + c1*ai*dphi0`
			return zoom(func, dfunc, args, xk, pk, phi0, dphi0, c1, c2, ai_last, ai, phi_ai_last, phi_ai, dphi_ai_last, dphi_ai)
		if print_flag == 1:
			print "\tSufficient decrease condition is OK"

		# Check if the curvature condition is met and if so, return the step length ai which satisfies the strong Wolfe conditions.
		if abs(dphi_ai) <= -c2*dphi0:
			if print_flag == 1:
				print "\tCurvature condition OK, returning xai"
			return xai
		if print_flag == 1:
			print "\tCurvature condition is violated"

		# Check if the gradient at ai is positive.
		# If so, the interval (ai-1, ai) will contain step lengths satisfying the strong Wolfe conditions.
		if dphi_ai >= 0.0:
			if print_flag == 1:
				print "\tGradient at ai is positive - zooming"
			# The arguments to zoom are ai followed by ai_last, because the function value at ai_last will be higher than at ai.
			return zoom(func, dfunc, args, xk, pk, phi0, dphi0, c1, c2, ai, ai_last, phi_ai, phi_ai_last, dphi_ai, dphi_ai_last)
		if print_flag == 1:
			print "\tGradient at ai is negative"

		# The strong Wolfe conditions are not met, and therefore interpolation between ai and a_max will be used to find a value for ai+1.
		if print_flag == 1:
			#print "\tStrong Wolfe conditions are not met, doing cubic interpolation"
			print "\tStrong Wolfe conditions are not met, doing quadratic interpolation"
		#ai_new = cubic_interpolate(ai_last, ai, phi_ai_last, dphi_ai_last, phi_ai, dphi_ai)
		ai_new = quadratic_interpolate(a1, phi0, dphi0, phi_ai)

		# Shift from ai+1 to ai.
		ai_last = ai
		xai_last = copy.deepcopy(xai)
		phi_ai_last = phi_ai
		dphi_ai_last = dphi_ai

		ai = ai_new
		i = i + 1


def zoom(func, dfunc, args, xk, pk, phi0, dphi0, c1, c2, a_lo, a_hi, phi_a_lo, phi_a_hi, dphi_a_lo, dphi_a_hi, print_flag=1):
	"""Find the minimum function value in the open interval (a_lo, a_hi)

	Algorithm 3.3, page 60, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	"""

	if print_flag == 1:
		print "\t\t<Zooming>"
	while 1:
		# Interpolate to find a trial step length aj between a_lo and a_hi.
		#aj = cubic_interpolate(a_lo, a_hi, phi_a_lo, dphi_a_lo, phi_a_hi, dphi_a_hi)
		#aj = cubic_interpolate(a_hi, a_lo, phi_a_hi, dphi_a_hi, phi_a_lo, dphi_a_lo)
		aj = quadratic_interpolate(a_lo, phi0, dphi0, phi_a_lo)

		# Determine the one dimensional function and gradient values at step length ai.
		xaj = xk + aj*pk
		phi_aj = apply(func, (xaj,)+args)
		dfaj = apply(dfunc, (xaj,)+args)
		dphi_aj = dot(dfaj, pk)

		if print_flag == 1:
			print "\t\ta_lo:      " + `a_lo`
			print "\t\tphi_a_lo:  " + `phi_a_lo`
			print "\t\tdphi_a_lo: " + `dphi_a_lo`
			print "\t\ta_hi:      " + `a_hi`
			print "\t\tphi_a_hi:  " + `phi_a_hi`
			print "\t\tdphi_a_hi: " + `dphi_a_hi`
			print "\t\taj:        " + `aj`
			print "\t\tphi_aj:    " + `phi_aj`
			print "\t\tdphi_aj:   " + `dphi_aj`

		# Check if the sufficient decrease condition is violated.
		if not phi_aj <= phi0 + c1*aj*dphi0:
			a_hi = aj
			phi_a_hi = phi_aj
			dphi_a_hi = dphi_aj
		else:
			# Check if the curvature condition is met and if so, return the step length ai which satisfies the strong Wolfe conditions.
			if abs(dphi_aj) <= -c2*dphi0:
				if print_flag == 1:
					print "\t\txaj: " + `xaj`
					print "\t\t<Finished zooming>"
				return xaj
	
			# Determine if a_hi needs to be reset.
			if dphi_aj*(a_hi - a_lo) >= 0.0:
				a_hi = a_lo
				phi_a_hi = phi_a_lo
				dphi_a_hi = dphi_a_lo

			a_lo = aj
			phi_a_lo = phi_aj
			dphi_a_lo = dphi_aj


def cubic_interpolate(ai_last, ai, phi_last, phi_prime_last, phi, phi_prime, print_flag=1):
	"""Cubic interpolation.

	Formula 3.43, page 57, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	"""

	d1 = phi_prime_last + phi_prime - 3.0 * ((phi_last - phi) / (ai_last - ai))
	d2 = sqrt(d1**2 - phi_prime_last*phi_prime)
	if print_flag == 1:
		print "\t\t\t<Cubic interpolation>"
		print "\t\t\td1:                               " + `phi_prime_last + phi_prime - 3.0 * ((phi_last - phi) / (ai_last - ai))`
		print "\t\t\td2:                               " + `sqrt(d1**2 - phi_prime_last*phi_prime)`
		print "\t\t\td1**2 - phi_prime_last*phi_prime: " + `d1**2 - phi_prime_last*phi_prime`
		print "\t\t\tai_new                            " + `ai - (ai - ai_last) * ((phi_prime + d2 - d1) / (phi_prime - phi_prime_last + 2.0*d2))`

	return ai - (ai - ai_last) * ((phi_prime + d2 - d1) / (phi_prime - phi_prime_last + 2.0*d2))


def quadratic_interpolate(a0, phi0, phi_prime0, phi_a0, print_flag=1):
	"""Quadratic interpolation.

	Formula 3.42, page 56, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	"""

	top = phi_prime0 * a0**2
	bottom = 2.0*(phi_a0 - phi0 - phi_prime0*a0)
	a1 = - top / bottom
	if print_flag == 1:
		print "\t\t\t<Quadratic interpolation>"
		print "\t\t\ttop:    " + `top`
		print "\t\t\tbottom: " + `bottom`
		print "\t\t\ta1:     " + `a1`

	return a1
