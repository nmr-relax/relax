from Numeric import Float64, dot, identity, matrixmultiply, outerproduct

from generic import Line_search, Min


def bfgs(func, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9):
	"""Quasi-Newton BFGS minimisation.

	"""

	min = Bfgs(func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta)
	if min.init_failure:
		print "Initialisation of minimisation has failed."
		return None
	results = min.minimise()
	return results


class Bfgs(Line_search, Min):
	def __init__(self, func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta):
		"""Class for Quasi-Newton BFGS minimisation specific functions.

		Unless you know what you are doing, you should call the function 'bfgs' rather than
		using this class.
		"""

		self.func = func
		self.dfunc = dfunc
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Minimisation options.
		#######################

		# Initialise.
		self.init_failure = 0

		# Minimisation options.
		if not self.line_search_option(min_options):
			self.init_failure = 1
			return

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Set the setup and update functions.
		self.setup = self.setup_bfgs
		self.update = self.update_bfgs

		# Line search function initialisation.
		self.init_line_functions()


	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		# Calculate the BFGS direction.
		self.pk = -matrixmultiply(self.Hk, self.dfk)

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup_bfgs(self):
		"""Setup function.

		Create the identity matrix I and calculate the function, gradient and initial BFGS
		inverse Hessian matrix.
		"""

		# Set the Identity matrix I.
		self.I = identity(len(self.xk), Float64)

		# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse Hessian matrix.
		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.Hk = self.I * 1.0


	def update_bfgs(self):
		"Function to update the function value, gradient vector, and the BFGS matrix"

		self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

		# sk and yk.
		sk = self.xk_new - self.xk
		yk = self.dfk_new - self.dfk
		dot_yk_sk = dot(yk, sk)

		# rho k.
		if dot_yk_sk == 0:
			raise NameError, "The BFGS matrix is indefinite.  This should not occur."
			rk = 1e99
		else:
			rk = 1.0 / dot_yk_sk

		# Preconditioning.
		if self.k == 0:
			self.Hk = dot_yk_sk / dot(yk, yk) * self.I

		self.Hk = matrixmultiply(self.I - rk*outerproduct(sk, yk), self.Hk)
		self.Hk = matrixmultiply(self.Hk, self.I - rk*outerproduct(yk, sk))
		self.Hk = self.Hk + rk*outerproduct(sk, sk)

		# Shift xk+1 data to xk.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk = self.dfk_new * 1.0
