from LinearAlgebra import inverse
from Numeric import Float64, dot, matrixmultiply, sqrt, zeros

from generic_minimise import generic_minimise
from line_search_functions import line_search_functions


class newton_cg(generic_minimise, line_search_functions):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9):
		"""Line search Newton conjugate gradient algorithm.

		Page 140 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

		The algorithm is:

		Given initial point x0.
		while 1:
			Compute a search direction pk by applying the CG method to Hk.pk = -gk,
			   starting from x0 = 0.  Terminate when ||rk|| <= min(0.5,sqrt(||gk||)), or
			   if negative curvature is encountered.
			Set xk+1 = xk + ak.pk, where ak satisfies the Wolfe, Goldstein, or Armijo
			   backtracking conditions.
			
		"""

		self.func = func
		self.dfunc = dfunc
		self.d2func = d2func
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Minimisation options.
		self.line_search_option(min_options)
		if self.init_failure: return

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Line search function initialisation.
		self.init_line_functions()


	def get_pk(self):
		"The CG algorithm."

		# Initial values at i = 0.
		xi = zeros(len(self.xk), Float64)
		ri = self.dfk * 1.0
		pi = -ri
		dot_ri = dot(ri, ri)
		len_g = sqrt(dot_ri)
		residual_test = min(0.5 * len_g, dot_ri)
		#residual_test = min(0.5, sqrt(len_g)) * len_g

		# Debugging.
		if self.print_flag == 2:
			print "Initial data:"
			print "\tx0: " + `xi`
			print "\tr0: " + `ri`
			print "\tp0: " + `pi`

		i = 0
		while 1:
			# Matrix product and curvature.
			Api = dot(self.d2fk, pi)
			curv = dot(pi, Api)

			# Negative curvature test.
			if curv <= 0.0:
				if i == 0:
					ai = dot_ri / curv
					return xi + ai*pi
				else:
					return xi
			if sqrt(dot_ri) <= residual_test:
				return xi

			# Conjugate gradient part
			ai = dot_ri / curv
			xi_new = xi + ai*pi
			ri_new = ri + ai*Api
			dot_ri_new = dot(ri_new, ri_new)
			bi_new = dot_ri_new / dot_ri
			pi_new = -ri_new + bi_new*pi

			# Debugging.
			if self.print_flag == 2:
				print "\nIteration i = " + `i`
				print "Api: " + `Api`
				print "Curv: " + `curv`
				print "ai: " + `ai`
				print "xi+1: " + `xi_new`
				print "ri+1: " + `ri_new`
				print "bi+1: " + `bi_new`
				print "pi+1: " + `pi_new`

			# Update i+1 to i.
			xi = xi_new * 1.0
			ri = ri_new * 1.0
			pi = pi_new * 1.0
			dot_ri = dot_ri_new
			i = i + 1



	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		# Get the pk vector.
		self.pk = self.get_pk()

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1


	def setup(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and hessian matrix are calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


	def update(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
