from Numeric import dot

def backtrack(func, args, xk, fk, dfk, pk, a_init=1.0, rho=0.5, c=1e-4):
	"""Backtracking line search.

	Procedure 3.1, page 41, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	Requires the gradient vector at point xk.


	Function options
	~~~~~~~~~~~~~~~~

	func		- The function to minimise.
	args		- The tuple of arguments to supply to the functions func.
	xk		- The parameter vector at minimisation step k.
	fk		- The function value at the point xk.
	dfk		- The function gradient vector at the point xk.
	pk		- The descent direction.
	a0		- Initial step length.
	rho		- The step length scaling factor (should be between 0 and 1).
	c		- Constant between 0 and 1 determining the slope for the sufficient decrease condition.


	Returned objects
	~~~~~~~~~~~~~~~~

	The parameter vector, minimised along the direction xk + ak.pk, to be used at k+1.


	Internal variables
	~~~~~~~~~~~~~~~~~~

	ai		- The step length at line search iteration i.
	xai		- The parameter vector at step length ai.
	fai		- The function value at step length ai.

	"""

	# Initialise values.
	ai = a_init

	while 1:
		xai = xk + ai*pk
		fai = apply(func, (xai,)+args)

		# Check if the sufficient decrease condition is met.  If not, scale the step length by rho.
		if fai <= fk + c*ai*dot(dfk, pk):
			return xai
		else:
			ai = rho*ai
