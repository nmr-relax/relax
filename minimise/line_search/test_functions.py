#! /usr/bin/python

from math import cos, sin, pi
from Numeric import array

from more_thuente import more_thuente

def run():
	print "Testing line minimiser using test function 1."
	xk = array([0.0])
	pk = array([1.0])
	args = ()
	a = more_thuente(func1, dfunc1, args, xk, pk, a_init=1e-3)
	print "The minimum is at " + `a`


def func1(alpha, beta=2.0):
	"""Test function 1.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The function is:
		                      alpha
		phi(alpha)  =  - ---------------
		                 alpha**2 + beta
	"""

	return - alpha[0]/(alpha[0]**2 + beta)


def dfunc1(alpha, beta=2.0):
	"""Derivative of test function 1.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The gradient is:
		                     2*alpha**2                 1
		phi'(alpha)  =  --------------------  -  ---------------
		                (alpha**2 + beta)**2     alpha**2 + beta

	"""

	temp = array([0.0])
	if alpha[0] > 1e90:
		return temp
	else:
		a = 2.0*(alpha[0]**2)/((alpha[0]**2 + beta)**2)
		print "a:        " + `a`
		b = 1.0/(alpha[0]**2 + beta)
		print "b:        " + `b`
		temp[0] = a - b
		return temp


def func2(alpha, beta=0.004):
	"""Test function 2.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The function is:

		phi(alpha)  =  (alpha + beta)**5 - 2(alpha + beta)**4
	"""

	return (alpha[0] + beta)**5 - 2.0*((alpha[0] + beta)**4)


def dfunc2(alpha, beta=0.004):
	"""Derivative of test function 2.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

	The gradient is:

		phi'(alpha)  =  5(alpha + beta)**4 - 8(alpha + beta)**3
	"""

	return 5.0*((alpha[0] + beta)**4) - 8.0*((alpha[0] + beta)**3)


def func3(alpha, beta=0.01, l=39.0):
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
	"""

	# Calculate phi0(alpha).
	if alpha[0] <= 1.0 - beta:
		phi0 = 1.0 - alpha[0]
	elif alpha[0] >= 1.0 + beta:
		phi0 = alpha[0] - 1.0
	else:
		phi0 = 0.5/beta * (alpha[0] - 1.0)**2 + 0.5*beta

	return phi0 + 2.0*(1.0 - beta)/(l*pi) * sin(0.5 * l * pi * alpha[0])


def dfunc3(alpha, beta=0.01, l=39.0):
	"""Derivative of test function 3.

	From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.

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

	# Calculate phi0'(alpha).
	if alpha[0] <= 1.0 - beta:
		phi0_prime = -1.0
	elif alpha[0] >= 1.0 + beta:
		phi0_prime = 1.0
	else:
		phi0_prime = (alpha[0] - 1.0)/beta

	return phi0_prime + (1.0 - beta) * cos(0.5 * l * pi * alpha[0])


run()
