from Numeric import Float64, zeros

from generic import minimise
#from bound_constraint import bound_constraint
from linear_constraint import linear_constraint


def method_of_multipliers(func, dfunc=None, d2func=None, args=(), x0=None, min_options=(), A=None, b=None, l=None, u=None, c=None, dc=None, d2c=None, mu0=1.0, tau0=1.0, lambda0=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
	"""The method of multipliers, also known as the augmented Lagrangian method.

	Three types of inequality constraint are supported.  These are linear, bound, and general
	constraints and must be setup as follows.  The vector x is the vector of model parameters.

	Currently equality constraints are not implemented.


	Linear constraints
	~~~~~~~~~~~~~~~~~~

	These are defined as:

		A.x >= b

	where:
		A is an m*n matrix where the rows are the transposed vectors, ai, of length n.  The
		elements of ai are the coefficients of the model parameters.

		x is the vector of model parameters of dimension n.

		b is the vector of scalars of dimension m.

		m is the number of constraints.

		n is the number of model parameters.

	eg if 0 <= q <= 1, q >= 1 - 2r, and 0 <= r, then:

		| 1  0 |            |  0 |
		|      |            |    |
		|-1  0 |   | q |    | -1 |
		|      | . |   | >= |    |
		| 1  2 |   | r |    |  1 |
		|      |            |    |
		| 0  1 |            |  2 |

	To use linear constraints both the matrix A and vector b need to be supplied.


	Bound constraints
	~~~~~~~~~~~~~~~~~

	These are defined as:

		l <= x <= u

	where l and u are the vectors of lower and upper bounds respectively.

	eg if 0 <= q <= 1, r >= 0, s <= 3, then:

		|  0  |    | q |    |  1  |
		|  0  | <= | r | <= | inf |
		|-inf |    | s |    |  3  |

	To use bound constraints both vectors l and u need to be supplied.


	General constraints
	~~~~~~~~~~~~~~~~~~~

	These are defined as:

		ci(x) >= 0

	where ci(x) are the constraint functions.

	To use general constrains the functions c, dc, and d2c need to be supplied.  The function c
	is the constraint function which should return the vector of constraint values.  The
	function dc is the constraint gradient function which should return the matrix of constraint
	gradient vectors.  The function d2c is the constraint Hessian function which should return
	the 3D matrix of constraint Hessians.

	"""

	min = Method_of_multipliers(func, dfunc, d2func, args, x0, min_options, A, b, l, u, c, dc, d2c, mu0, tau0, lambda0, func_tol, maxiter, full_output, print_flag)
	if min.init_failure:
		print "Initialisation of minimisation has failed."
		return None
	results = min.minimise()
	return results



class Method_of_multipliers:
	def __init__(self, func, dfunc, d2func, args, x0, min_options, A, b, l, u, c, dc, d2c, mu0, tau0, lambda0, func_tol, maxiter, full_output, print_flag):
		"""Class for Newton minimisation specific functions.

		Unless you know what you are doing, you should call the function
		'method_of_multipliers' rather than using this class.
		"""

		# Linear constraints.
		if A != None and b != None:
			self.A = A
			self.b = b
			self.linear_constraint = linear_constraint(self.A, self.b)
			self.c = self.linear_constraint.func
			self.dc = self.linear_constraint.dfunc
			self.d2c = None
			self.m = len(self.b)

		# Bound constraints.
		elif l != None and u != None:
			print "Bound constraints are not implemented yet."
			self.init_failure = 1
			return
			self.l = l
			self.u = u
			#self.bound_constraint = bound_constraint(self.l, self.u)
			#self.c = self.bound_constraint.func
			#self.dc = self.bound_constraint.dfunc
			#self.d2c = None
			self.m = 2.0*len(self.l)

		# General constraints.
		elif c != None and dc != None and d2c != None:
			self.c = c
			self.dc = dc
			self.d2c = d2c

		# Incorrectly supplied constraints.
		else:
			print "The constraints have been incorreclty supplied."
			self.init_failure = 1
			return

		# Arguments.
		self.func = func
		self.dfunc = dfunc
		self.d2func = d2func
		self.args = args
		self.xk = x0
		self.min_options = min_options
		self.mu = mu0
		self.tau = tau0
		self.lambda_k = lambda0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Minimisation options.
		#######################

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Initialise data structures.
		self.L = 0.0
		self.dL = zeros(len(self.xk), Float64)
		self.d2L = zeros((len(self.xk), len(self.xk)), Float64)
		self.test_structure = zeros(self.m)


	def func_LA(self):
		"""The augmented Lagrangian function.

		The equation is:

			L(x, lambda_k; muk) = f(x) + sum(psi(ci(x), lambdai_k; muk))

		where:

                                        /  -s.t + t^2/(2m)	if t - ms <= 0,
			psi(t, s; m) = <
			                \  -ms^2/2		otherwise.
		"""

		self.L = apply(self.func, (self.xk,)+self.args)
		self.ck = apply(self.c, (self.xk,))

		for i in range(self.m):
			if self.ck[i] - self.mu*self.lambda_k[i] <= 0:
				self.L = self.L  -  0.5 * self.mu * self.lambda_k[i]**2
				self.test_structure[i] = 1
			else:
				self.L = self.L  -  lambda_k[i] * self.ck[i]  +  0.5 * self.ck[i]**2 / self.mu
				self.test_structure[i] = 0

		return self.L


	def func_dLA(self):
		"""The augmented Lagrangian gradient.

		"""

		self.dL = apply(self.dfunc, (self.xk,)+self.args)
		self.dck = apply(self.dc, (self.xk,))

		for i in range(self.m):
			if self.test_structure[i]:
				self.dL = self.dL - (self.lambda_k[i] - self.ck[i] / self.mu) * self.dck[i]

		return self.dL


	def func_d2LA(self):
		"""The augmented Lagrangian Hessian.

		"""

		raise NameError, "Incomplete code."
		self.d2L = apply(self.d2func, (self.xk,)+self.args)
		self.d2ck = apply(self.d2c, (self.xk,))

		return self.d2L


	def func_d2LA_simple(self):
		"""The augmented Lagrangian Hessian.

		This function has been simplified by assuming that the constraint Hessian is zero.
		"""

		raise NameError, "Incomplete code."
		self.d2L = apply(self.d2func, (self.xk,)+self.args)
		return self.d2L


	def minimise(self):
		"""Method of multipliers algorithm.

		Page 515 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

		The algorithm is:

		Given u0 > 0, tolerance t0 > 0, starting points x0s and lambda0
		while 1:
			Find an approximate minimiser xk of LA(.,lambdak; uk), starting at xks, and
			   terminating when the augmented Lagrangian gradeint <= tk
			Final convergence test
			Update Lagrange multipliers using formula 17.58
			Chouse new penalty parameter uk+1 within (0, uk)
			Set starting point for the next iteration to xk+1s = xk
			k = k + 1
		"""

		# Start the iteration counters.
		self.k = 0
		self.j = 0

		# Iterate until the local minima is found.
		while 1:
			# Print out.
			if self.print_flag:
				if self.print_flag == 2:
					print "\n\n<<<Main iteration k=" + `self.k` + " >>>"
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)

			# Unconstrained minimisation sub-loop.
			results = minimise(func_LA, dfunc=func_dLA, d2func=func_d2LA, args=args, x0=self.xk, min_algor=min_algor, min_options=min_options, maxiter=maxiter, full_output=1, print_flag=print_flag)
			self.xk_new, self.fk_new, j, f, g, h, self.warning = results
			self.j = self.j + j
			self.f_count = self.f_count + f
			self.g_count = self.g_count + g
			self.h_count = self.h_count + h
			if self.warning != None:
				break

			# Convergence test.
			if self.tests():
				break

			# Update function.
			self.update_multipliers()

			# Iteration counter update.
			self.xk = self.xk_new * 1.0
			self.fk = self.fk_new
			self.k = self.k + 1


		if self.full_output:
			try:
				return self.xk_new, self.fk_new, self.k+1, self.f_count, self.g_count, self.h_count, self.warning
			except AttributeError:
				return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			try:
				return self.xk_new
			except AttributeError:
				return self.xk


	def tests(self):
		"""Default base class convergence test function.

		Test if the minimum function tolerance between fk and fk+1 has been reached.
		"""

		# Test the function tolerance.
		if abs(self.fk_new - self.fk) <= self.func_tol:
			if self.print_flag == 2:
				print "fk:          " + `self.fk`
				print "fk+1:        " + `self.fk_new`
				print "|fk+1 - fk|: " + `abs(self.fk_new - self.fk)`
				print "tol:         " + `self.func_tol`
			self.warning = "Function tol reached."
			return 1
		else:
			if self.print_flag == 2:
				print "Pass function tol test."


	def update_multipliers(self):
		"""Lagrange multiplier update function.

		The update is given by the following formula:

			lambdai_k+1 = max(lambdai_k - ci(xk)/mu, 0)
		"""

		for i in range(self.m):
			self.lambda_k[i] = max(self.lambda_k[i] - self.ck[i]/self.mu, 0.0)
