from trust_region import trust_region


def cauchy_point(func, dfunc, d2func, x0, args=(), tol=1e-5, maxiter=1000, full_output=0, print_flag=1):
	"""Cauchy Point trust-region algorithm.

	Page 70 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	The Cauchy point is defined by:

		                delta_k
		pCk  =  - tau_k ------- dfk
		                ||dfk||

	where:
		delta_k is the trust region radius,
		dfk is the gradient vector,

		         / 1							if dfk . Bk . dfk <= 0
		tau_k = <
		         \ min(||dfk||**2/(delta_k . dfk . Bk . dfk), 1)	otherwise.
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

