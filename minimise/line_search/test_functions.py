from math import cos, sin, pi

def test_func1(alpha, beta=2.0, deriv=0):
	"""Test function 1.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The function is:
		                      alpha
		phi(alpha)  =  - ---------------
		                 alpha**2 + beta

	The gradient is:
		                     2*alpha**2                 1
		phi'(alpha)  =  --------------------  -  ---------------
		                (alpha**2 + beta)**2     alpha**2 + beta


	"""

	# Calculate the gradient value.
	if deriv:
		a = 2.0*(alpha**2)/((alpha**2 + beta)**2)
		b = 1.0/(alpha**2 + beta)
		return a - b

	# Calculate the function value.
	else:
		return - alpha/(alpha**2 + beta)


def test_func2(alpha, beta=0.004, deriv=0):
	"""Test function 2.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The function is:

		phi(alpha)  =  (alpha + beta)**5 - 2(alpha + beta)**4


	The gradient is:

		phi'(alpha)  =  5(alpha + beta)**4 - 8(alpha + beta)**3



	"""

	# Calculate the gradient value.
	if deriv:
		return 5.0*((alpha + beta)**4) - 8.0*((alpha + beta)**3)

	# Calculate the function value.
	else:
		return (alpha + beta)**5 - 2.0*((alpha + beta)**4)


def test_func3(alpha, beta=0.01, l=39.0, deriv=0):
	"""Test function 3.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The function is:

		                             2(1 - beta)       / l*pi         \ 
		phi(alpha)  =  phi0(alpha) + ----------- . sin | ---- . alpha |
		                                l*pi           \  2           /

		where:
			                /  1 - alpha,				if alpha <= 1 - beta,
			                |
			                |  alpha - 1,				if alpha >= 1 + beta,
			phi0(alpha) =  <
			                |   1                    1
			                | ------(alpha - 1)**2 + - beta,	if alpha in [1 - beta, 1 + beta].
			                \ 2*beta                 2


	The gradient is:


		                                               / l*pi         \ 
		phi(alpha)  =  phi0'(alpha) + (1 - beta) . cos | ---- . alpha |
		                                               \  2           /

		where:
			                 /  -1,			if alpha <= 1 - beta,
			                 |
			                 |  1,			if alpha >= 1 + beta,
			phi0'(alpha) =  <
			                 | alpha - 1
			                 | ---------,		if alpha in [1 - beta, 1 + beta].
			                 \   beta



	"""

	# Calculate the gradient value.
	if deriv:
		# Calculate phi0'(alpha).
		if alpha <= 1.0 - beta:
			phi0_prime = -1.0
		elif alpha >= 1.0 + beta:
			phi0_prime = 1.0
		else:
			phi0_prime = (alpha - 1.0)/beta

		return phi0_prime + (1.0 - beta) * cos(0.5 * l * pi * alpha)

	# Calculate the function value.
	else:
		# Calculate phi0(alpha).
		if alpha <= 1.0 - beta:
			phi0 = 1.0 - alpha
		elif alpha >= 1.0 + beta:
			phi0 = alpha - 1.0
		else:
			phi0 = 0.5/beta * (alpha - 1.0)**2 + 0.5*beta

		return phi0 + 2.0*(1.0 - beta)/(l*pi) * sin(0.5 * l * pi * alpha)

