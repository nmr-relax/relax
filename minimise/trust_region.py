from Numeric import dot, sqrt


def trust_region(delta_max=1e5, delta0=1.0, eta=0.2):
	"""An algorithm for trust region radius selection.

	Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
	"""

	while 1:
		# Optain pk.
		pk = get_pk()

		# Evaluate rho.
		rho = calc_rho(func, xk, pk, dfk, Bk)

		# Calculate the Euclidean norm of pk.
		norm_pk = sqrt(dot(pk, pk))

		# Choose the trust region radius for the next iteration.
		# Rho is close to zero or negative, therefore the trust region is shrunk.
		if rho < 0.25:
			delta_new = 0.25 * norm_pk
		# Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
		elif rho > 0.75 and norm_pk == delta:
			delta_new = min(2.0*delta, delta_max)
		# Rho is positive but not close to one, therefore the trust region is unaltered.
		else:
			delta_new = delta

		# Choose the position for the next iteration.
		if rho > eta:
			xk_new = xk + pk
		else:
			xk_new = xk

		# Update.
		delta = delta_new
		xk = xk_new


def calc_rho(func, xk, pk, dfk, Bk):
	"""Function to calculate the ratio rho used to choose the trust region radius.

	The ratio is defined as:

		        f(xk) - f(xk + pk)
		rho  =  ------------------
		          mk(0) - mk(pk)

	Where the numerator is called the actual reduction and the denominator is the predicted reduction.
	"""

	# Actual reduction.
	fk = apply(func, (xk,)+args)
	f_pk = apply(func, (xk + pk,)+args)
	act_red = f - f_p

	# Predicted reduction.
	mk_pk = fk + dot(dfk, pk) + 0.5 * dot(pk, dot(Bk, pk))
	pred_red = f - mk_pk

	# Rho.
	rho = act_red / pred_red
	return rho
