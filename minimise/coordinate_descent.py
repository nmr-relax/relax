from Numeric import Float64, copy, dot, identity, zeros

from generic_line_search import generic_line_search
from generic_minimise import generic_minimise


class coordinate_descent(generic_line_search, generic_minimise):
	def __init__(self):
		"Class for back-and-forth coordinate descent minimisation specific functions."


	def minimise(self, *min_args):
		"Back-and-forth coordinate descent minimisation."

		# Generic data initialisation.
		self.min_args = min_args
		self.init_data()

		# The initial function value and gradient vector.
		self.update_data()

		# Set a0.
		self.a0 = 1.0

		# Create the coordinate descent directions, and initialise the coordinate descent iteration number and direction flag.
		self.cd_dir = identity(len(self.xk), Float64)
		self.n = 0
		self.back = 0

		# Line search constants for the Wolfe conditions.
		self.mu = 0.0001
		self.eta = 0.1

		# Minimisation.
		self.generic_minimise()

		if self.full_output:
			return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
		else:
			return self.xk


	def backup_current_data(self):
		"Function to backup the current data dfk into dfk_last."

		self.dfk_last = copy.deepcopy(self.dfk)


	def dir(self):
		"Return  the back-and-forth coordinate search direction for iteration k."

		# The direction pk is forced to be a descent direction.
		if dot(self.dfk, self.cd_dir[self.n]) > 0.0:
			self.pk = -self.cd_dir[self.n]
		else:
			self.pk = self.cd_dir[self.n]

		# Update the coordinate descent iteration number and direction flag.
		if not self.back:
			if self.n < len(self.xk) - 1:
				self.n = self.n + 1
			else:
				self.back = 1
				self.n = self.n - 1
		else:
			if self.n > 0:
				self.n = self.n - 1
			else:
				back = 0
				self.n = self.n + 1


	def update_data(self):
		"Function to update the function value, gradient vector, and hessian matrix"

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.d2fk = None

def crap():
	# Initial values before the first iteration.
	xk = x0
	fk = apply(func, (x0,)+args)
	dfk = apply(dfunc, (x0,)+args)


	# Start the iteration counter.
	k = 0

	# Debugging code.
	if print_flag == 1:
		k2 = 0

	# Iterate until the local minima is found.
	while 1:
		# Debugging code.
		if print_flag >= 1:
			if print_flag == 2:
				print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
			else:
				if k2 == 100:
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", k, "Min params:", `xk`, "Function value:", `fk`)
					k2 = 0

		# Calculate the initial step length a0.
		if k == 0:
			a0 = 1.0
		else:
			a0 = alpha * dot(dfk_old, pk_old) / dot(dfk, pk)

		# Backtracking line search.
		if match('^[Bb]ack', line_search_algor):
			alpha = backtrack(func, args, xk, fk, dfk, pk, a_init=a0)
		# Nocedal and Wright interpolation based line search.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', line_search_algor):
			alpha = nocedal_wright_interpol(func, args, xk, fk, dfk, pk, a_init=a0, mu=0.001, print_flag=0)
		# Nocedal and Wright line search for the Wolfe conditions.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', line_search_algor):
			alpha = nocedal_wright_wolfe(func, dfunc, args, xk, fk, dfk, pk, a_init=a0, mu=0.001, eta=0.1, print_flag=0)
		# More and Thuente line search.
		elif match('^[Mm]ore[ _][Tt]huente$', line_search_algor):
			alpha = more_thuente(func, dfunc, args, xk, fk, dfk, pk, a_init=a0, mu=0.001, eta=0.1, print_flag=1)
		# No line search.
		elif match('^[Nn]one$', line_search_algor):
			alpha = a0
		# No match to line search string.
		else:
			raise NameError, "The line search algorithm " + line_search_algor + " is not setup for back-and-forth coordinate descent minimisation.\n"

		# Find the parameter vector, function value, and gradient vector for iteration k+1.
		xk_new = xk + alpha * pk
		fk_new = apply(func, (xk_new,)+args)
		dfk_new = apply(dfunc, (xk_new,)+args)

		# Test for the local minimum.
		if abs(fk - fk_new) <= tol:
			if print_flag:
				print "fk: " + `fk`
				print "fk_new: " + `fk_new`
				print "<Fin>"

		# Update to the next iteration number.
		k = k + 1
		dfk_old = copy.deepcopy(dfk)
		pk_old = copy.deepcopy(pk)
		xk = xk_new
		fk = fk_new
		dfk = copy.deepcopy(dfk_new)

		# Debugging code.
		if print_flag == 1:
			k2 = k2 + 1
