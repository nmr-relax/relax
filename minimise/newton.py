from LinearAlgebra import cholesky_decomposition, eigenvectors, inverse, solve_linear_equations
from Numeric import Float64, array, dot, identity, matrixmultiply, sort, sqrt, transpose
from re import match

from generic_minimise import generic_minimise
from line_search_functions import line_search_functions


class newton(generic_minimise, line_search_functions):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, min_options=(), func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9, mach_acc=1e-16):
		"""Class for Newton minimisation specific functions.

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
		self.mach_acc = mach_acc

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Minimisation options.
		#######################

		# Initialise.
		self.line_search_algor = None
		self.hessian_mod = None
		self.init_failure = 0

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1; return

		# Test that no more thant 2 options are given.
		if len(min_options) > 2:
			print "A maximum of two minimisation options is allowed (the line search algorithm and the Hessian modification)."
			self.init_failure = 1; return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.line_search_algor == None and self.valid_line_search(opt):
				self.line_search_algor = opt
			elif self.hessian_mod == None and self.valid_hessian_mod(opt):
				self.hessian_mod = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid line search algorithm or Hessian modification."
				self.init_failure = 1; return

		# Default line search algorithm.
		if self.line_search_algor == None:
			self.line_search_algor = 'More Thuente'

		# Default Hessian modification.
		if self.hessian_mod == None:
			self.hessian_mod = 'Chol'

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Constants.
		self.n = len(self.xk)
		self.I = identity(len(self.xk))

		# Set the setup and update functions.
		self.setup = self.setup_newton
		self.update = self.update_newton

		# Line search and Hessian modification initialisation.
		self.init_line_functions()
		self.init_hessian_mod_funcs()


	def cholesky(self, return_matrix=0):
		"""Cholesky with added multiple of the identity.

		Algorithm 6.3 from page 145 of 'Numerical Optimization' by Jorge Nocedal and Stephen
		J. Wright, 1999.

		Returns the modified Newton step.
		"""

		# Calculate the Frobenius norm of the Hessian and the minimum diagonal value.
		norm = 0.0
		min_aii = 1e99
		for i in range(self.n):
			min_aii = min(self.d2fk[i, i], min_aii)
			for j in range(self.n):
				norm = norm + self.d2fk[i, j]**2
		norm = sqrt(norm)
		half_norm = norm / 2.0

		if min_aii > 0.0:
			tk = 0.0
		else:
			tk = half_norm

		if self.print_flag == 2:
			print "Frobenius norm: " + `norm`
			print "min aii: " + `min_aii`
			print "tk: " + `tk`

		k = 0
		while 1:
			if self.print_flag == 2:
				print "Iteration " + `k`

			# Calculate the matrix A + tk.I
			matrix = self.d2fk + tk * self.I

			try:
				self.L = cholesky_decomposition(matrix)
				if self.print_flag == 2:
					print "\tCholesky matrix L: " + `self.L`
				break
			except "LinearAlgebraError":
				if self.print_flag == 2:
					print "\tLinearAlgebraError, matrix is not positive definite."
				tk = max(2.0*tk, half_norm)

			k = k + 1

		# Calculate the Newton direction.
		y = solve_linear_equations(self.L, self.dfk)
		if return_matrix:
			return -solve_linear_equations(transpose(self.L), y), matrix
		else:
			return -solve_linear_equations(transpose(self.L), y)


	def eigenvalue(self, return_matrix=0):
		"""The eigenvalue Hessian modification.

		This modification is based on equation 6.14 from page 144 of 'Numerical
		Optimization' by Jorge Nocedal and Stephen J. Wright, 1999.

		Returns the modified Newton step.
		"""

		if self.print_flag == 2:
			print "d2fk: " + `self.d2fk`

		eigen = eigenvectors(self.d2fk)
		eigenvals = sort(eigen[0])
		tau = max(0.0, self.delta - eigenvals[0])
		matrix = self.d2fk + tau * self.I

		# Debugging.
		if self.print_flag == 2:
			print "Eigenvalues: " + `eigenvals`
			print "tau: " + `tau`
			print "d2fk: " + `matrix`

		# Calculate the Newton direction.
		if return_matrix:
			return -matrixmultiply(inverse(matrix), self.dfk), matrix
		else:
			return -matrixmultiply(inverse(matrix), self.dfk)


	def gmw(self, return_matrix=0):
		"""The Gill, Murray, and Wright modified Cholesky algorithm.

		Algorithm 6.5 from page 148 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright,
		1999.

		Returns the modified Newton step.
		"""

		#self.d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)

		# Calculate gamma(A) and xi(A).
		gamma = 0.0
		xi = 0.0
		for i in range(self.n):
			gamma = max(abs(self.d2fk[i, i]), gamma)
			for j in range(i+1, self.n):
				xi = max(abs(self.d2fk[i, j]), xi)

		# Calculate delta and beta.
		delta = self.mach_acc * max(gamma + xi, 1)
		if self.n == 1:
			beta = 1e99
		else:
			beta = sqrt(max(gamma, xi / sqrt(self.n**2 - 1.0), self.mach_acc))

		# Initialise data structures.
		a = self.d2fk
		r = 0.0 * self.d2fk
		e = 0.0 * self.xk
		P = 1.0 * self.I

		if self.print_flag == 2:
			old_eigen = eigenvectors(self.d2fk)
			print "d2fk: " + `self.d2fk`

		# Main loop.
		for j in range(self.n):
			# Row and column swapping.
			p = 1.0 * self.I
			q = j
			for i in range(j, self.n):
				if abs(a[q, q]) <= abs(a[i, i]):
					q = i
			if q != j:
				# Modify the permutation matrices.
				temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
				p[:, q], P[:, q] = p[:, j], P[:, j]
				p[:, j], P[:, j] = temp_p, temp_P

				# Permute a and r.
				a = dot(p, dot(a, p))
				r = dot(p, dot(r, p))

			# Calculate ljj.
			theta_j = 0.0
			if j < self.n-1:
				for i in range(j+1, self.n):
					theta_j = max(theta_j, abs(a[j, i]))
			dj = max(abs(a[j, j]), (theta_j/beta)**2, delta)
			r[j, j] = sqrt(dj)

			# Calculate e (not really needed!).
			e[j] = dj - a[j, j]

			# Calculate l and a.
			for i in range(j+1, self.n):
				r[j, i] = a[j, i] / r[j, j]
				for k in range(j+1, i+1):
					a[k, i] = a[k, i] - r[j, i]*r[j, k]

		# The Cholesky factor.
		self.L = dot(P, transpose(r))

		if self.print_flag == 2:
			print "e: " + `dot(P, dot(e, transpose(P)))`
			temp = dot(self.L,transpose(self.L))
			print "d2fk:\n" + `self.d2fk`
			print "d2fk reconstruted:\n" + `temp`
			eigen = eigenvectors(temp)
			print "Old eigenvalues: " + `old_eigen[0]`
			print "New eigenvalues: " + `eigen[0]`
			sorted = sort(old_eigen[0])
			if sorted[0] > 0.0:
				for i in range(len(e)):
					if e[i] != 0.0:
						print "\n### Fail ###\n"
						import sys
						sys.exit()

		# Calculate the Newton direction.
		y = solve_linear_equations(self.L, self.dfk)
		if return_matrix:
			return -solve_linear_equations(transpose(self.L), y), dot(self.L,transpose(self.L))
		else:
			return -solve_linear_equations(transpose(self.L), y)


	def init_hessian_mod_funcs(self):
		"Initialise the Hessian modification functions."

		if self.hessian_mod == None:
			if self.print_flag:
				print "Hessian modification:  Unmodified Hessian."
			self.get_pk = self.unmodified_hessian
		elif match("^[Ee]igen", self.hessian_mod):
			if self.print_flag:
				print "Hessian modification:  Eigenvalue modification."
			self.get_pk = self.eigenvalue
			self.delta = sqrt(self.mach_acc)
		elif match("^[Cc]hol", self.hessian_mod):
			if self.print_flag:
				print "Hessian modification:  Cholesky with added multiple of the identity."
			self.get_pk = self.cholesky
		elif match("^[Gg][Mm][Ww]", self.hessian_mod):
			if self.print_flag:
				print "Hessian modification:  The Gill, Murray, and Wright modified Cholesky algorithm."
			self.get_pk = self.gmw


	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		# Calculate the Newton direction.
		self.pk = self.get_pk()

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1

		# Debugging.
		if self.print_flag == 2:
			print "pk: " + `self.pk`
			print "alpha: " + `self.alpha`
			print "xk: " + `self.xk`
			print "xk+1: " + `self.xk_new`
			print "fk: " + `self.fk`
			print "fk+1: " + `self.fk_new`
			eigen = eigenvectors(self.d2fk)
			for i in range(len(self.d2fk)):
				print "B[" + `i` + ", " + `i` + "] = " + `self.d2fk[i, i]`
			print "Eigenvalues: " + `eigen[0]`


	def setup_newton(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and Hessian matrix are
		calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


	def unmodified_hessian(self, return_matrix=0):
		"Calculate the pure Newton direction."

		if return_matrix:
			return -matrixmultiply(inverse(self.d2fk), self.dfk), self.d2fk
		else:
			return -matrixmultiply(inverse(self.d2fk), self.dfk)


	def update_newton(self):
		"Function to update the function value, gradient vector, and Hessian matrix"

		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


	def valid_hessian_mod(self, mod):
		"Test if the string 'mod' is a valid Hessian modification."

		if mod == None or match("^[Ee]igen", mod) or match("^[Cc]hol", mod) or match("^[Gg][Mm][Ww]", mod):
			return 1
		else:
			return 0
