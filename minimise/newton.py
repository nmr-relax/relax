from LinearAlgebra import cholesky_decomposition, eigenvectors, inverse, solve_linear_equations
from Numeric import Float64, array, dot, identity, matrixmultiply, sort, sqrt, transpose
from re import match

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class newton(generic_line_search, generic_minimise):
	def __init__(self, func, dfunc=None, d2func=None, args=(), x0=None, line_search_algor=None, hessian_mod=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.9, mach_acc=1e-16):
		"Class for Newton minimisation specific functions."

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

		if not line_search_algor:
			raise NameError, "No line search algorithm has been supplied."
		elif not hessian_mod:
			raise NameError, "The hessian modification has not been specified."
		else:
			self.line_search_algor = line_search_algor

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

		# Set the setup and update functions.
		self.setup = self.setup_newton
		self.update = self.update_newton

		# The hessian modification functions.
		if match("^[Ee]igen", hessian_mod):
			self.hessian_modification = self.eigenvalue
			self.delta = sqrt(self.mach_acc)
		elif match("^[Cc]hol", hessian_mod):
			self.hessian_modification = self.cholesky
		elif match("^[Mm]odified[ -_][Cc]holesky$", hessian_mod) or match("^[Mm]od$", hessian_mod):
			self.hessian_modification = self.modified_cholesky

		# Constants.
		self.n = len(self.xk)
		self.I = identity(len(self.xk))


	def cholesky(self):
		"""Cholesky with added multiple of the identity.

		Algorithm 6.3 from page 145.
		"""

		# Calculate the Frobenius norm of the hessian and the minimum diagonal value.
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
				R = cholesky_decomposition(matrix)
				if self.print_flag == 2:
					print "\tCholesky matrix R: " + `R`
				self.d2fk = matrix
				return
			except "LinearAlgebraError":
				if self.print_flag == 2:
					print "\tLinearAlgebraError, matrix is not positive definite."
				tk = max(2.0*tk, half_norm)

			k = k + 1


	def eigenvalue(self):
		"""The eigenvalue hessian modification.

		This modification is based on equation 6.14 from page 144.
		"""

		if self.print_flag == 2:
			print "d2fk: " + `self.d2fk`

		eigen = eigenvectors(self.d2fk)
		eigenvals = sort(eigen[0])
		tau = max(0.0, self.delta - eigenvals[0])
		self.d2fk = self.d2fk + tau * self.I

		# Debugging.
		if self.print_flag == 2:
			print "Eigenvalues: " + `eigenvals`
			print "tau: " + `tau`
			print "d2fk: " + `self.d2fk`


	def modified_cholesky(self):
		"""Modified Cholesky hessian modification.

		Algorithm 6.5 from page 148.

		Somehow the data structures l, d, and c can be stored in self.d2fk!
		"""

		# Debugging (REMOVE!!!).
		#self.d2fk = array([[-0.004, 2, 1], [2, 6, 3], [1, 3, 4]], Float64)
		if self.print_flag == 2:
			print "d2fk: " + `self.d2fk`
			eigen = eigenvectors(self.d2fk)
			eigenvals = sort(eigen[0])
			print "Eigenvalues: " + `eigenvals`

		# Calculate gamma(A) and xi(A).
		gamma = 0.0
		xi = 0.0
		for i in range(self.n):
			gamma = max(abs(self.d2fk[i, i]), gamma)
			for j in range(i+1, self.n):
				xi = max(abs(self.d2fk[i, j]), xi)

		# Calculate delta and beta.
		delta = self.mach_acc * max(gamma + xi, 1)
		beta = sqrt(max(gamma, xi / sqrt(self.n**2 - 1.0), self.mach_acc))

		# Initialise data structures.
		d2fk_orig = 1.0 * self.d2fk
		c = 0.0 * self.d2fk
		d = 0.0 * self.xk
		l = 1.0 * self.I
		e = 0.0 * self.xk
		P = 1.0 * self.I

		# Initial diagonal elements of c.
		for k in range(self.n):
			c[k, k] = self.d2fk[k, k]

		# Main loop.
		for j in range(self.n):
			if self.print_flag == 2:
				print "\n<j: " + `j` + ">"

			# Row and column swapping.
			p = 1.0 * self.I
			q = j
			for i in range(j, self.n):
				if abs(c[q, q]) <= abs(c[i, i]):
					q = i
			if self.print_flag == 2:
				print "Row and column swapping."
				print "i range: " + `range(j, self.n)`
				print "q: " + `q`
				print "a: " + `self.d2fk`
				print "c: " + `c`
				print "d: " + `d`
				print "l: " + `l`
			if q != j:
				# Modify the permutation matrices.
				temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
				p[:, q], P[:, q] = p[:, j], P[:, j]
				p[:, j], P[:, j] = temp_p, temp_P

				# Permute both c and d2fk.
				c = dot(p, dot(c, p))
				self.d2fk = dot(p, dot(self.d2fk, p))

				if self.print_flag == 2:
					print "p: " + `p`
					print "a(mod): " + `self.d2fk`
					print "c(mod): " + `c`
					print "d(mod): " + `d`
					print "l(mod): " + `l`

			# Calculate the elements of l.
			if self.print_flag == 2:
				print "\nCalculate the elements of l."
				print "s range: " + `range(j)`
			for s in range(j):
				if self.print_flag == 2:
					print "s: " + `s`
				l[j, s] = c[j, s] / d[s]
			if self.print_flag == 2:
				print "l: " + `l`

			# Calculate c[i, j].
			if self.print_flag == 2:
				print "\nCalculate c[i, j]."
				print "i range: " + `range(j+1, self.n)`
			for i in range(j+1, self.n):
				sum = 0.0
				for s in range(j):
					if self.print_flag == 2:
						print "s range: " + `range(j)`
					sum = sum + l[j, s] * c[i, s]
				c[i, j] = self.d2fk[i, j] - sum
			if self.print_flag == 2:
				print "c: " + `c`

			# Calculate d.
			if self.print_flag == 2:
				print "\nCalculate d."
			theta_j = 0.0
			if j < self.n-1:
				if self.print_flag == 2:
					print "j < n, " + `j` + " < " + `self.n-1`
					print "i range: " + `range(j+1, self.n)`
				for i in range(j+1, self.n):
					theta_j = max(theta_j, abs(c[i, j]))
			else:
				if self.print_flag == 2:
					print "j >= n, " + `j` + " >= " + `self.n-1`
			d[j] = max(abs(c[j, j]), (theta_j/beta)**2, delta)
			if self.print_flag == 2:
				print "theta_j: " + `theta_j`
				print "d: " + `d`

			# Calculate c[i, i].
			if self.print_flag == 2:
				print "\nCalculate c[i, i]."
			if j < self.n-1:
				if self.print_flag == 2:
					print "j < n, " + `j` + " < " + `self.n-1`
					print "i range: " + `range(j+1, self.n)`
				for i in range(j+1, self.n):
					c[i, i] = c[i, i] - c[i, j]**2 / d[j]
			else:
				if self.print_flag == 2:
					print "j >= n, " + `j` + " >= " + `self.n-1`
			if self.print_flag == 2:
				print "c: " + `c`

			# Calculate e.
			e[j] = d[j] - c[j, j]

		for i in range(self.n):
			self.d2fk[i, i] = self.d2fk[i, i] + e[i]
		self.d2fk = dot(P, dot(self.d2fk, transpose(P)))

		# Debugging.
		if self.print_flag == 2:
			print "\nFin:"
			print "gamma(A): " + `gamma`
			print "xi(A): " + `xi`
			print "delta: " + `delta`
			print "beta: " + `beta`
			print "c: " + `c`
			print "d: " + `d`
			print "l: " + `l`
			temp = 0.0 * self.I
			for i in range(len(d)):
				temp[i, i] = d[i]
			print "m: " + `dot(l, sqrt(temp))`
			print "mmT: " + `dot(dot(l, sqrt(temp)), transpose(dot(l, sqrt(temp))))`
			print "P: " + `P`
			print "e: " + `e`
			print "d2fk: " + `self.d2fk`
			eigen = eigenvectors(self.d2fk)
			eigenvals = sort(eigen[0])
			print "Eigenvalues: " + `eigenvals`
			import sys
			sys.exit()


	def new_param_func(self):
		"""The new parameter function.

		Find the search direction, do a line search, and get xk+1 and fk+1.
		"""

		if self.print_flag == 2:
			print "Unmodified pk: " + `-matrixmultiply(inverse(self.d2fk), self.dfk)`
		# Hessian modifications.
		self.hessian_modification()

		# Calculate the Newton direction.
		#self.pk = -matrixmultiply(inverse(self.d2fk), self.dfk)
		self.pk = -solve_linear_equations(self.d2fk, self.dfk)

		# Take a steepest descent step if self.pk is not a descent dir.
		#if dot(self.dfk, self.pk) >= 0.0:
		#	print "Step: " + `self.k` + ".  Switching to a steepest descent step to avoid an ascent direction."
		#	self.pk = -self.dfk

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
			eigenvals = sort(eigen[0])
			for i in range(len(self.d2fk)):
				print "B[" + `i` + ", " + `i` + "] = " + `self.d2fk[i, i]`
			print "Eigenvalues: " + `eigenvals`


	def setup_newton(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and hessian matrix are calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


	def update_newton(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
