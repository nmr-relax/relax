import sys

from Numeric import copy, dot

from interpolate import cubic, quadratic_fafbga, quadratic_gagb

quadratic = quadratic_fafbga
secant = quadratic_gagb


def more_thuente(func, func_prime, args, x, p, a_init=1.0, mu=0.001, eta=0.1, phi_min=0.0, dmax=1.1, dmin=7.0/12.0):
	"""A line search algorithm from More and Thuente.

	More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient decrease.
	ACM Trans. Math. Softw. 20, 286-307.


	Internal variables
	~~~~~~~~~~~~~~~~~~

	a0, the null sequence data structure containing the following keys:
		'a'		- 0
		'phi'		- phi(0)
		'phi_prime'	- phi'(0)
		'psi'		- psi(0)
		'psi_prime'	- psi'(0)

	a, the sequence data structure containing the following keys:
		'a'		- alpha
		'phi'		- phi(alpha)
		'phi_prime'	- phi'(alpha)
		'psi'		- psi(alpha)
		'psi_prime'	- psi'(alpha)

	Ik, the interval data structure containing the following keys:
		'a'		- The current interval Ik = [al, au]
		'phi'		- The interval [phi(al), phi(au)]
		'phi_prime'	- The interval [phi'(al), phi'(au)]
		'psi'		- The interval [psi(al), psi(au)]
		#'psi_prime'	- The interval [psi'(al), psi'(au)]

	Ik_lim, the limiting interval [a_min, a_max].
	"""

	print "\n<Line search initial values>"

	# Initialise values.
	k = 0
	type_flag = 1
	a0 = {}
	a0['a'] = 0.0
	a0['phi'] = func_phi(func, args, x, 0.0, p)
	a0['phi_prime'] = func_phi_prime(func_prime, args, x, 0.0, p)
	a0['psi'] = - mu * a0['phi_prime'] * 0.0
	a0['psi_prime'] = (1.0 - mu) * a0['phi_prime']

	if a0['phi_prime'] >= 0:
		raise NameError, "The gradient at point 0 is positive, ie p is not a descent direction."

	print_seq_data('init', a0)

	# Initialise sequence data.
	a = {}
	a['a'] = a_init
	a['phi'] = func_phi(func, args, x, a['a'], p)
	a['phi_prime'] = func_phi_prime(func_prime, args, x, a['a'], p)
	a['psi'] = - mu * a0['phi_prime'] * a['a']
	a['psi_prime'] = a0['phi_prime'] - mu * a0['phi_prime']

	print_seq_data(k, a)

	# Initialise interval data.
	Ik = {}
	Ik['a'] = [0.0, 1e99]
	Ik['phi'] = [func_phi(func, args, x, Ik['a'][0], p), func_phi(func, args, x, Ik['a'][1], p)]
	Ik['phi_prime'] = [func_phi_prime(func_prime, args, x, Ik['a'][0], p), func_phi_prime(func_prime, args, x, Ik['a'][1], p)]
	Ik['psi'] = [- mu * a0['phi_prime'] * Ik['a'][0], - mu * a0['phi_prime'] * Ik['a'][1]]
	Ik['psi_prime'] = [(1.0 - mu) * a0['phi_prime'], (1.0 - mu) * a0['phi_prime']]

	Ik_lim = [0.0, 1.0 / mu * ((a0['phi'] - phi_min) / -a0['phi_prime'])]

	print_int_data(k, Ik)

	while 1:
		print "\n<Line search iteration k = " + `k` + " >"

		# Type flag, 0 - phi, 1 - psi.
		if a['psi'] <= 0.0 and a['phi_prime'] >= 0.0:
			type_flag = 0

		# Choose a safeguarded ak in set Ik which is a subset of [a_min, a_max].
		print "Choosing a safeguarded ak in set Ik which is a subset of [a_min, a_max]."
		a_new = {}
		if type_flag == 0:
			a_new['a'] = choose_a(Ik['a'][0], Ik['a'][1], a['a'], Ik['phi'][0], Ik['phi'][1], a['phi'], Ik['phi_prime'][0], Ik['phi_prime'][1], a['phi_prime'])
		else:
			a_new['a'] = choose_a(Ik['a'][0], Ik['a'][1], a['a'], Ik['psi'][0], Ik['psi'][1], a['psi'], Ik['psi_prime'][0], Ik['psi_prime'][1], a['psi_prime'])

		# Calculate new values.
		a_new['phi'] = func_phi(func, args, x, a_new['a'], p)
		a_new['phi_prime'] = func_phi_prime(func_prime, args, x, a_new['a'], p)
		a_new['psi'] = - mu * a0['phi_prime'] * a_new['a']
		a_new['psi_prime'] = a0['phi_prime'] - mu * a0['phi_prime']

		print_seq_data(k, a_new)

		# Test for convergence.
		print "Testing for convergence using the strong Wolfe conditions."
		if converged(mu, eta, a_new, a0):
			print "<Line search has converged>\n"
			return a_new

		# Update the interval Ik.
		print "Updating the interval Ik."
		Ik_new = update_Ik(a_new, Ik)

		print_int_data(k, Ik_new)

		# Safeguarding.
		print "Safeguarding."
		safeguard()

		# Shift data from k+1 to k.
		k = k + 1
		a = a_new
		Ik = Ik_new

		#if k > 2:
		#	sys.exit()


def print_seq_data(k, a):
	"Temp func for debugging."

	print "Sequence data printout:"
	print "   Iteration:   " + `k`
	print "   a:           " + `a['a']`
	print "   phi:         " + `a['phi']`
	print "   phi_prime:   " + `a['phi_prime']`
	print "   psi:         " + `a['psi']`
	print "   psi_prime:   " + `a['psi_prime']`


def print_int_data(k, Ik):
	"Temp func for debugging."

	print "Interval data printout:"
	print "   Iteration:   " + `k`
	print "   Ik:          " + `Ik['a']`
	print "   phi_I:       " + `Ik['phi']`
	print "   phi_I_prime: " + `Ik['phi_prime']`
	print "   psi_I:       " + `Ik['psi']`


def choose_a(al, au, at, fl, fu, ft, gl, gu, gt, d=0.66):
	"""Trial value selection.

	fl, fu, ft, gl, gu, and gt are the function and gradient values at the interval end points al and au, and at the trial point at.
	ac is the minimiser of the cubic that interpolates fl, ft, gl, and gt.
	aq is the minimiser of the quadratic that interpolates fl, ft, and gl.
	as is the minimiser of the quadratic that interpolates fl, gl, and gt.

	The trial value selection is divided into four cases.

	Case 1: ft > fl.  In this case compute ac and aq, and set

		       / ac,			if |ac - al| < |aq - al|,
		at+ = <
		       \ 1/2(aq + ac),		otherwise.


	Case 2: ft <= fl and gt.gl < 0.  In this case compute ac and as, and set

		       / ac,			if |ac - at| >= |as - at|,
		at+ = <
		       \ as,			otherwise.


	Case 3: ft <= fl and gt.gl >= 0, and |gt| <= |gl|.  In this case at+ is chosen by extrapolating the function values at al and at, so the trial value at+
	lies outside th interval with at and al as endpoints.  Compute ac and as.

		If the cubic tends to infinity in the direction of the step and the minimum of the cubic is beyound at, set

			       / ac,			if |ac - at| < |as - at|,
			at+ = <
			       \ as,			otherwise.

		Otherwise set at+ = as.


		Redefine at+ by setting

			       / min{at + d(au - at), at+},		if at > al.
			at+ = <
			       \ max{at + d(au - at), at+},		otherwise,
	
		for some d < 1.


	Case 4: ft <= fl and gt.gl >= 0, and |gt| > |gl|.  In this case choose at+ as the minimiser of the cubic that interpolates fu, ft, gu, and gt.

	"""

	# Case 1.
	if ft > fl:
		# Compute ac and aq.
		ac = cubic(al, at, fl, ft, gl, gt)
		aq = quadratic(al, at, fl, ft, gl)

		# Test if neither ac nor aq lie in I+.
		if ac < al or ac > au:
			raise NameError, "ac not in the interval I+"
		if aq < al or aq > au:
			raise NameError, "aq not in the interval I+"

		# Return at+.
		if abs(ac - al) < abs(aq - al):
			print "\tCase 1. at_new = ac"
			return ac
		else:
			print "\tCase 1. at_new = 1/2(aq + ac)"
			return 0.5*(aq + ac)


	# Case 2.
	elif ft <= fl and gt * gl < 0.0:
		# Compute ac and as.
		ac = cubic(al, at, fl, ft, gl, gt)
		as = secant(al, at, gl, gt)

		# Test if neither ac nor aq lie in I+.
		if ac < al or ac > au:
			raise NameError, "ac not in the interval I+"
		if as < al or as > au:
			raise NameError, "as not in the interval I+"

		# Debugging code (remove).
		print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\tI+: " + `Ik['a']`
		print "\tac: " + `ac`
		print "\tas: " + `as`
		sys.exit()

		# Return at+.
		if abs(ac - at) >= abs(as - at):
			print "\tCase 2. at_new = ac"
			return ac
		else:
			print "\tCase 2. at_new = as"
			return as


	# Case 3.
	elif ft <= fl and gt * gl >= 0.0 and abs(gt) <= abs(gl):
		# Compute ac and as.
		ac = cubic(al, at, fl, ft, gl, gt)
		as = secant(al, at, gl, gt)

		# Debugging code (remove).
		print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\tI+: " + `Ik['a']`
		print "\tac: " + `ac`
		print "\tas: " + `as`
		sys.exit()

		# Test if the minimum of the cubic is beyond at.
		if ac > at:
			if abs(ac - at) < abs(as - at):
				at_new = ac
			else:
				at_new = as
		else:
			at_new = as

		# Redefine at+.
		at_redef = at + d*(au - at)
		if at > al:
			# Return min{at + d(au - at), at+}.
			if at_redef < at_new:
				return at_redef
			else:
				return at_new
		else:
			# Return max{at + d(au - at), at+}.
			if at_redef > at_new:
				return at_redef
			else:
				return at_new


	# Case 4.
	elif ft <= fl and gt * gl >= 0.0 and abs(gt) > abs(gl):
		print "\tCase 4."
		sys.exit()
		return cubic(au, at, fu, ft, gu, gt)


	# Cases 1 to 4 are not satisfied.
	else:
		raise NameError, "Should not be here"


def converged(mu, eta, a, a0):
	"""Test for convergence using the strong Wolfe conditions.

	The conditions are:
		phi(alpha) <= phi(0) + mu.phi'(0).a
		|phi'(a)| <= eta.|phi'(0)|
	"""

	if a['phi'] <= a0['phi'] + mu * a['a'] * a0['phi_prime'] and abs(a['phi_prime']) <= eta * abs(a0['phi_prime']):
		return 1
	else:
		return 0


def func_phi(func, args, x, a, p):
	"""Calculate the function value phi(alpha).

	Formula:
		phi(alpha) = f(x + alpha*p)

	"""

	print "\tEvaluating the function phi(alpha)."
	return apply(func, (x + a*p,)+args)


def func_phi_prime(func_prime, args, x, a, p):
	"""Calculate the gradient value phi'(alpha).

	Formula:
		phi'(alpha) = f'(x + alpha*p)

	"""

	print "\tEvaluating the gradient phi'(alpha)."
	f_prime = apply(func_prime, (x + a*p,)+args)
	return dot(f_prime, p)


def func_psi(mu, a, a0):
	"""Calculate the function value psi(alpha).

	Formula:
		psi(alpha) = phi(alpha) - phi(0) - mu * phi'(0) * alpha

	"""
	print "\tEvaluating the function psi(alpha)."
	return a['phi'] - a0['phi'] - mu * a0['phi_prime'] * a['a']


def func_psi_prime(mu, a, a0):
	"""Calculate the gradient value psi'(alpha).

	Formula:
		psi'(alpha) = phi'(alpha) - mu * phi'(0)

	"""

	print "\tEvaluating the gradient psi'(alpha)."
	return a['phi_prime'] - mu * a0['phi_prime']


def safeguard():
	pass


def update_Ik(a, Ik):
	"""Updating algorithm.

	Given a trial value at in I, the endpoints al+ and au+ of the updated interval I+ are determined as follows:
		Case U1: If psi(at) > psi(al), then al+ = al and au+ = at.
		Case U2: If psi(at) <= psi(al) and psi'(at)(al - at) > 0, then al+ = at and au+ = au.
		Case U3: If psi(at) <= psi(al) and psi'(at)(al - at) < 0, then al+ = at and au+ = al.
	"""

	Ik_new = Ik

	# Case U1.
	if a['psi'] > Ik['psi'][0]:
		print "\tCase U1"
		Ik_new['a'][1]         = a['a']
		Ik_new['phi'][1]       = a['phi']
		Ik_new['phi_prime'][1] = a['phi_prime']
		Ik_new['psi'][1]       = a['psi']

	# Case U2.
	elif a['psi'] <= Ik['psi'][0] and a['psi_prime'] * (Ik['a'][0] - a['a']) > 0.0:
		print "\tCase U2"
		Ik_new['a'][0]         = a['a']
		Ik_new['phi'][0]       = a['phi']
		Ik_new['phi_prime'][0] = a['phi_prime']
		Ik_new['psi'][0]       = a['psi']

	# Case U3.
	elif a['psi'] <= Ik['psi'][0] and a['psi_prime'] * (Ik['a'][0] - a['a']) < 0.0:
		print "\tCase U3"
		Ik_new['a'][0]         = a['a']
		Ik_new['phi'][0]       = a['phi']
		Ik_new['phi_prime'][0] = a['phi_prime']
		Ik_new['psi'][0]       = a['psi']

		Ik_new['a'][1]         = Ik['a'][0]
		Ik_new['phi'][1]       = Ik['phi'][0]
		Ik_new['phi_prime'][1] = Ik['phi_prime'][0]
		Ik_new['psi'][1]       = Ik['psi'][0]
	else:
		raise NameError, "It is physically impossible to be here!"

	return Ik_new
