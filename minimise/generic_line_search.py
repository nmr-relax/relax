from re import match

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


class generic_line_search:
	def __init__(self):
		"Class containing non-specific line search algorithm code."


	def new_param_func(self):
		"""Pure Newton minimisation.

		Function options
		~~~~~~~~~~~~~~~~

		func			- The function to minimise.
		dfunc			- The function which returns the gradient vector.
		d2func			- The function which returns the hessian matrix.
		x0			- The initial parameter vector.
		args			- The tuple of arguments to supply to the functions func, dfunc, and d2func.
		tol			- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
		maxiter			- The maximum number of iterations.
		full_output		- A flag specifying what should be returned (see below).
		print_flag		- A flag specifying how much information should be printed to standard output during minimisation:

		The print flag corresponds to:
			0 - No output.
			1 - Minimal output.
			2 - Full output.


		Returned objects
		~~~~~~~~~~~~~~~~

		If full_output=0, then only the minimised parameter vector is returned.
		If full_output=1, then the minimised parameter vector, function value at the minimum, number of iterations, and a warning flag are returned.
		The warning flag corresponds to:
			0 - Minimisation terminated successfully.
			1 - Maximum number of iterations have been reached.


		Internal variables
		~~~~~~~~~~~~~~~~~~

		k	- The iteration number.
		xk	- Parameter vector at iteration number k.
		fk	- Function value at xk.
		fk_last	- Function value at xk-1.
		dfk	- Gradient vector at xk.
		d2fk	- Hessian matrix at xk.
		pk	- Descent direction of the iteration number k.

		"""

		# Initialise.
		fc, gc, hc = 0, 0, 0

		# Calculate the search direction for iteration k.
		self.dir()

		# Get a0.
		try:
			self.get_a0()
		except AttributeError:
			"a0 should not be changed."

		# Backtracking line search.
		if match('^[Bb]ack', self.line_search_algor):
			self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
		# Nocedal and Wright interpolation based line search.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor):
			self.alpha, fc = nocedal_wright_interpol(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, print_flag=0)
		# Nocedal and Wright line search for the Wolfe conditions.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor):
			self.alpha, fc, gc = nocedal_wright_wolfe(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		# More and Thuente line search.
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor):
			self.alpha, fc, gc = more_thuente(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		# No line search.
		elif match('^[Nn]one$', self.line_search_algor):
			self.alpha = self.a0
		# No match to line search string.
		else:
			raise NameError, "The line search algorithm " + self.line_search_algor + " is not coded.\n"

		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc
		self.h_count = self.h_count + hc

		# Find the new parameter vector.
		self.xk_new = self.xk + self.alpha * self.pk
