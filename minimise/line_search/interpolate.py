from Numeric import sqrt

def cubic(a, b, fa, fb, ga, gb):
	"""Cubic interpolation using f(a), f(b), g(a), and g(b).

	Equations
	~~~~~~~~~

	f(a) = a'a**3 + b'a**2 + c'a + d'
	f(b) = a'b**3 + b'b**2 + c'b + d'
	g(a) = 3a'a**2 + 2b'a + c'
	g(b) = 3a'b**2 + 2b'b + c'


	Interpolation
	~~~~~~~~~~~~~

	The extrema are the roots of the quadratic equation:

		3a'*alpha**2 + 2b'*alpha + c' = 0

	The cubic interpolant is given by the formula:

		                   g(b) + beta2 - beta1
		ac = b - (b - a) . ---------------------
		                   g(b) - g(a) + 2*beta2

	where:

		                          f(a) - f(b)
		beta1 = g(a) + g(b) - 3 . -----------
		                             a - b

		if a < b:
			beta2 = sqrt(beta1**2 - g(a).g(b))
		else:
			beta2 = -sqrt(beta1**2 - g(a).g(b))

	"""


	beta1 = ga + gb - 3.0*(fa - fb)/(a - b)
	if a < b:
		beta2 = sqrt(beta1**2 - ga*gb)
	else:
		beta2 = -sqrt(beta1**2 - ga*gb)

	alpha = b - (b - a)*(gb + beta2 - beta1)/(gb - ga + 2.0*beta2)
	return alpha


def quadratic_fafbga(a, b, fa, fb, ga):
	"""Quadratic interpolation using f(a), f(b), and g(a).

	The extremum of the quadratic is given by:

		       2af(a) + b**2g(a) - a(2f(b) + ag(a))
		aq  =  ------------------------------------
		           2(f(a) - f(b) + (b - a)g(a))
	"""

	top = 2.0*a*fa + b**2*ga - a*(2.0*fb + a*ga)
	bottom = 2.0*(fa - fb + (b - a)*ga)
	if bottom == 0.0:
		return 1e99
	else:
		return top / bottom


def quadratic_gagb(a, b, ga, gb):
	"""Quadratic interpolation using g(a) and g(b).

	The extremum of the quadratic is given by:

		       bg(a) - ag(b)
		aq  =  -------------
		        g(a) - g(b)
	"""

	temp = ga - gb
	if temp == 0.0:
		return 1e99
	else:
		return (b*ga - a*gb)/(ga - gb)
