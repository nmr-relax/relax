# This module contains the following functions and base classes:
#	minimise:		The generic minimisation function.
#	Min:			The base class containing the main iterative minimisation loop and
#		a few other base class functions.
#	Line_search:		The base class containing the generic line search functions.
#	Trust_region:		The base class containing the generic trust-region functions.
#	Conjugate_gradient:	The base class containing the generic conjugate gradient functions.


# Inbuilt python modules.
#########################
from LinearAlgebra import inverse
from Numeric import dot, matrixmultiply, sqrt
from re import match


# Line search functions.
########################

from minimise.line_search.backtrack import backtrack
from minimise.line_search.nocedal_wright_interpol import nocedal_wright_interpol
from minimise.line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from minimise.line_search.more_thuente import more_thuente





# The generic minimisation function.
####################################

def generic_minimise(func=None, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, full_output=0, print_flag=0, print_prefix=""):
	"""Generic minimisation function.

	This is a generic function which can be used to access all minimisers using the same set of
	function arguments.  These are the function tolerance value for convergence tests, the
	maximum number of iterations, a flag specifying which data structures should be returned,
	and a flag specifying the amount of detail to print to screen.


	Arguments
	~~~~~~~~~

	func:	The function which returns the function value.
	dfunc:	The function which returns the gradient vector.
	d2func:	The function which returns the Hessian matrix or approximation.
	args:	The tuple of arguments to supply to the functions func, dfunc, and d2func.
	x0:	The vector of initial parameter value estimates (as an array).

	min_algor:	A string specifying which minimisation technique to use.
	min_options:	A tuple to pass to the minimisation function as the min_options keyword.

	func_tol:	The function tolerance value.  Once the function value between iterations
		decreases below this value, minimisation is terminated.
	maxiter:	The maximum number of iterations.

	full_output:	A flag specifying which data structures should be returned.  The following
		values will return, in tuple form, the following data:
			0 - xk
			1 - (xk, fk, k, f_count, g_count, h_count, warning)
		where the data names correspond to:
			xk:		The array of minimised parameter values.
			fk:		The minimised function value.
			k:		The number of iterations.
			f_count:	The number of function calls.
			g_count:	The number of gradient calls.
			h_count:	The number of Hessian calls.
			warning:	The warning string.
	print_flag:	A flag specifying how much information should be printed to standard output
		during minimisation.  The print flag corresponds to:
			0 - No output.
			1 - Minimal output.
			2 - Full output.


	Minimisation algorithms
	~~~~~~~~~~~~~~~~~~~~~~~

	A minimisation function is selected if the string min_algor matches a certain pattern.
	Because the python regular expression 'match' statement is used, various values of min_algor
	can be used to select the same minimisation algorithm.  Below is a list of the minimisation
	algorithms available together with the corresponding patterns.  Here is a quick description
	of pattern syntax.  The square brakets [] are used to specify a sequence of characters to
	match to a single character within 'min_algor'.  For example Newton minimisation is carried
	out if a match to the pattern '[Nn]ewton' occurs.  Therefore setting min_algor to either
	'Newton' or 'newton' will select the Newton algorithm.  The symbol '^' placed at the start
	of the pattern means match to the start of 'min_algor' while the symbol '$' placed at the
	end of the pattern means match to the end of 'min_algor'.  For example, one of the
	Levenberg-Marquardt patterns is '^[Ll][Mm]$'.  The algorithm is selected by setting
	min_algor to 'LM' or 'lm'.  Placing any characters before or after these strings will result
	in the algorithm not being selected.

	To select an algorithm set min_algor to a string which matches the given pattern.

	Parameter initialisation methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Grid search                       | '^[Gg]rid'                                          |
	| Fixed parameter values            | '^[Ff]ixed'                                         |
	|-----------------------------------|-----------------------------------------------------|


	Unconstrained line search methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Back-and-forth coordinate descent | '^[Cc][Dd]$' or '^[Cc]oordinate[ _-][Dd]escent$'    |
	| Steepest descent                  | '^[Ss][Dd]$' or '^[Ss]teepest[ _-][Dd]escent$'      |
	| Quasi-Newton BFGS                 | '^[Nn]ewton$'                                       |
	| Newton                            | '^[Bb][Ff][Gg][Ss]$'                                |
	| Newton-CG                         | '^[Nn]ewton[ _-][Cc][Gg]$' or '^[Nn][Cc][Gg]$'      |
	|-----------------------------------|-----------------------------------------------------|


	Unconstrained trust-region methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Cauchy point                      | '^[Cc]auchy'                                        |
	| Dogleg                            | '^[Dd]ogleg'                                        |
	| CG-Steihaug                       | '^[Cc][Gg][-_ ][Ss]teihaug' or '^[Ss]teihaug'       |
	| Exact trust region                | '^[Ee]xact'                                         |
	|-----------------------------------|-----------------------------------------------------|


	Unconstrained conjugate gradient methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Fletcher-Reeves                   | '^[Ff][Rr]$' or '^[Ff]letcher[-_ ][Rr]eeves$'       |
	| Polak-Ribi�re                     | '^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'         |
	| Polak-Ribi�re +                   | '^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'     |
	| Hestenes-Stiefel                  | '^[Hh][Ss]$' or '^[Hh]estenes[-_ ][Ss]tiefel$'      |
	|-----------------------------------|-----------------------------------------------------|


	Miscellaneous unconstrained methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Simplex                           | '^[Ss]implex$'                                      |
	| Levenberg-Marquardt               | '^[Ll][Mm]$' or '^[Ll]evenburg-[Mm]arquardt$'       |
	|-----------------------------------|-----------------------------------------------------|


	Constrained methods:
	___________________________________________________________________________________________
	|                                   |                                                     |
	| Minimisation algorithm            | Patterns                                            |
	|-----------------------------------|-----------------------------------------------------|
	|                                   |                                                     |
	| Method of Multipliers             | '^[Mm][Oo][Mm]$' or '[Mm]ethod of [Mm]ultipliers$'  |
	|-----------------------------------|-----------------------------------------------------|



	Minimisation options
	~~~~~~~~~~~~~~~~~~~~

	This section needs to be completed.
	"""

	# Parameter initialisation methods.
	###################################

	# Grid search.
	if match('^[Gg]rid', min_algor):
		from minimise.grid import grid
		xk, fk, k = grid(func=func, args=args, grid_ops=min_options, print_flag=print_flag)
		if full_output:
			results = (xk, fk, k, k, 0, 0, None)
		else:
			results = xk

	# Fixed parameter values.
	elif match('^[Ff]ixed', min_algor):
		if print_flag:
			if print_flag >= 2:
				print print_prefix
			print print_prefix
			print print_prefix + "Fixed initial parameter values"
			print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		xk = min_options
		fk = apply(func, (xk,)+args)
		if full_output:
			results = (xk, fk, 1, 1, 0, 0, None)
		else:
			results = xk


	# Unconstrained line search algorithms.
	#######################################

	# Back-and-forth coordinate descent minimisation.
	elif match('^[Cc][Dd]$', min_algor) or match('^[Cc]oordinate[ _-][Dd]escent$', min_algor):
		from minimise.coordinate_descent import coordinate_descent
		results = coordinate_descent(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', min_algor):
		from minimise.steepest_descent import steepest_descent
		results = steepest_descent(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', min_algor):
		from minimise.bfgs import bfgs
		results = bfgs(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Newton minimisation.
	elif match('^[Nn]ewton$', min_algor):
		from minimise.newton import newton
		results = newton(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Newton-CG minimisation.
	elif match('^[Nn]ewton[ _-][Cc][Gg]$', min_algor) or match('^[Nn][Cc][Gg]$', min_algor):
		from minimise.ncg import ncg
		results = ncg(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


	# Unconstrained trust-region algorithms.
	########################################

	# Cauchy point minimisation.
	elif match('^[Cc]auchy', min_algor):
		from minimise.cauchy_point import cauchy_point
		results = cauchy_point(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Dogleg minimisation.
	elif match('^[Dd]ogleg', min_algor):
		from minimise.dogleg import dogleg
		results = dogleg(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# CG-Steihaug minimisation.
	elif match('^[Cc][Gg][-_ ][Ss]teihaug', min_algor) or match('^[Ss]teihaug', min_algor):
		from minimise.steihaug_cg import steihaug
		results = steihaug(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Exact trust region minimisation.
	elif match('^[Ee]xact', min_algor):
		from minimise.exact_trust_region import exact_trust_region
		results = exact_trust_region(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


	# Unconstrained conjugate gradient algorithms.
	##############################################

	# Fletcher-Reeves conjugate gradient minimisation.
	elif match('^[Ff][Rr]$', min_algor) or match('^[Ff]letcher[-_ ][Rr]eeves$', min_algor):
		from minimise.fletcher_reeves_cg import fletcher_reeves
		results = fletcher_reeves(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Polak-Ribi�re conjugate gradient minimisation.
	elif match('^[Pp][Rr]$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere$', min_algor):
		from minimise.polak_ribiere_cg import polak_ribiere
		results = polak_ribiere(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Polak-Ribi�re + conjugate gradient minimisation.
	elif match('^[Pp][Rr]\+$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere\+$', min_algor):
		from minimise.polak_ribiere_plus_cg import polak_ribiere_plus
		results = polak_ribiere_plus(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Hestenes-Stiefel conjugate gradient minimisation.
	elif match('^[Hh][Ss]$', min_algor) or match('^[Hh]estenes[-_ ][Ss]tiefel$', min_algor):
		from minimise.hestenes_stiefel_cg import hestenes_stiefel
		results = hestenes_stiefel(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


	# Miscellaneous unconstrained algorithms.
	#########################################

	# Simplex minimisation.
	elif match('^[Ss]implex$', min_algor):
		from minimise.simplex import simplex
		results = simplex(func=func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
		from minimise.levenberg_marquardt import levenberg_marquardt
		results = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


	# Constrainted algorithms.
	##########################

	# Method of Multipliers.
	elif match('^[Mm][Oo][Mm]$', min_algor) or match('[Mm]ethod of [Mm]ultipliers$', min_algor):
		from minimise.method_of_multipliers import method_of_multipliers
		results = method_of_multipliers(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# No match to minimiser string.
	###############################

	else:
		print print_prefix + "Minimiser type set incorrectly.  The minimiser " + min_algor + " is not programmed.\n"
		return


	# Finish.
	#########

	if print_flag and results != None:
		print ""
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
			print print_prefix + "Parameter values: " + `xk`
			print print_prefix + "Function value:   " + `fk`
			print print_prefix + "Iterations:       " + `k`
			print print_prefix + "Function calls:   " + `f_count`
			print print_prefix + "Gradient calls:   " + `g_count`
			print print_prefix + "Hessian calls:    " + `h_count`
			if warning:
				print print_prefix + "Warning:          " + warning
			else:
				print print_prefix + "Warning:          None"
		else:
			print print_prefix + "Parameter values: " + `results`

	return results





# The generic minimisation base class (containing the main iterative loop).
###########################################################################

class Min:
	def __init__(self):
		"""Base class containing the main minimisation iterative loop algorithm.

		The algorithm is defined in the minimise function.
		Also supplied are generic setup, convergence tests, and update functions.
		"""


	def double_test(self, fk_new, fk, gk):
		"""Default base class function for both function and gradient convergence tests.

		Test if the minimum function tolerance between fk and fk+1 has been reached as well
		as if the minimum gradient tolerance has been reached.
		"""

		# Test the function tolerance.
		if abs(fk_new - fk) <= self.func_tol:
			if self.print_flag >= 2:
				print "\n" + self.print_prefix + "Function tolerance reached."
				print self.print_prefix + "fk:          " + `fk`
				print self.print_prefix + "fk+1:        " + `fk_new`
				print self.print_prefix + "|fk+1 - fk|: " + `abs(fk_new - fk)`
				print self.print_prefix + "tol:         " + `self.func_tol`
			return 1
		
		# Test the gradient tolerance.
		elif sqrt(dot(gk, gk)) <= self.grad_tol:
			if self.print_flag >= 2:
				print "\n" + self.print_prefix + "Gradient tolerance reached."
				print self.print_prefix + "gk+1:     " + `gk`
				print self.print_prefix + "||gk+1||: " + `sqrt(dot(gk, gk))`
				print self.print_prefix + "tol:      " + `self.grad_tol`
			return 1


	def func_test(self, fk_new, fk, gk):
		"""Default base class function for the function convergence test.

		Test if the minimum function tolerance between fk and fk+1 has been reached.
		"""

		# Test the function tolerance.
		if abs(fk_new - fk) <= self.func_tol:
			if self.print_flag >= 2:
				print "\n" + self.print_prefix + "Function tolerance reached."
				print self.print_prefix + "fk:          " + `fk`
				print self.print_prefix + "fk+1:        " + `fk_new`
				print self.print_prefix + "|fk+1 - fk|: " + `abs(fk_new - fk)`
				print self.print_prefix + "tol:         " + `self.func_tol`
			return 1


	def grad_test(self, fk_new, fk, gk):
		"""Default base class function for the gradient convergence test.

		Test if the minimum gradient tolerance has been reached.  Minimisation will also
		terminate if the function value difference between fk and fk+1 is zero.  This
		modification is essential for the quasi-Newton techniques.
		"""

		# Test the gradient tolerance.
		if sqrt(dot(gk, gk)) <= self.grad_tol:
			if self.print_flag >= 2:
				print "\n" + self.print_prefix + "Gradient tolerance reached."
				print self.print_prefix + "gk+1:     " + `gk`
				print self.print_prefix + "||gk+1||: " + `sqrt(dot(gk, gk))`
				print self.print_prefix + "tol:      " + `self.grad_tol`
			return 1

		# No change in function value (prevents the minimiser from iterating without moving).
		elif fk_new - fk == 0.0:
			if self.print_flag >= 2:
				print "\n" + self.print_prefix + "Function difference of zero."
				print self.print_prefix + "fk_new - fk = 0.0"
			return 1


	def hessian_type_and_mod(self, min_options, default_type='Newton', default_mod='Chol'):
		"""Hessian type and modification options.

		Function for sorting out the minimisation options when either the Hessian type or
		Hessian modification can be selected.
		"""

		# Initialise.
		self.hessian_type = None
		self.hessian_mod = None

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print self.print_prefix + "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1
			return

		# Test that no more thant 2 options are given.
		if len(min_options) > 2:
			print self.print_prefix + "A maximum of two minimisation options is allowed (the Hessian type and Hessian modification)."
			self.init_failure = 1
			return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.hessian_type == None and (match('[Bb][Ff][Gg][Ss]', opt) or match('[Nn]ewton', opt)):
				self.hessian_type = opt
			elif self.hessian_mod == None and self.valid_hessian_mod(opt):
				self.hessian_mod = opt
			else:
				print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid Hessian type or modification."
				self.init_failure = 1
				return

		# Default Hessian type.
		if self.hessian_type == None:
			self.hessian_type = default_type

		# Make sure that no Hessian modification is used with the BFGS matrix.
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type) and self.hessian_mod != None:
			print self.print_prefix + "When using the BFGS matrix, Hessian modifications should not be used."
			self.init_failure = 1
			return

		# Default Hessian modification when the Hessian type is Newton.
		if match('[Nn]ewton', self.hessian_type) and self.hessian_mod == None:
			self.hessian_mod = default_mod

		# Print the Hessian type info.
		if self.print_flag:
			if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
				print self.print_prefix + "Hessian type:  BFGS"
			else:
				print self.print_prefix + "Hessian type:  Newton"


	def minimise(self):
		"""Main minimisation iterative loop algorithm.

		This algorithm is designed to be compatible with all iterative minimisers.  The
		outline is:

		k = 0
		Setup function
		while 1:
			New parameter function
			Convergence tests
			Update function
			k = k + 1
		"""

		# Start the iteration counter.
		self.k = 0
		if self.print_flag:
			self.k2 = 0
			print ""   # Print a new line.

		# Setup function.
		self.setup()

		# Iterate until the local minima is found.
		while 1:
			# Print out.
			if self.print_flag:
				out = 0
				if self.print_flag >= 2:
					print "\n" + self.print_prefix + "Main iteration k=" + `self.k`
					out = 1
				else:
					if self.k2 == 100:
						self.k2 = 0
					if self.k2 == 0:
						out = 1
				if out == 1:
					print self.print_prefix + "%-3s%-8i%-4s%-65s%-4s%-20s" % ("k:", self.k, "xk:", `self.xk`, "fk:", `self.fk`)

			# Get xk+1 (new parameter function).
			#self.new_param_func()
			try:
				self.new_param_func()
			except "LinearAlgebraError", message:
				self.warning = "LinearAlgebraError: " + message + " (fatal minimisation error)."
				break
			except OverflowError, message:
				if type(message.args[0]) == int:
					text = message.args[1]
				else:
					text = message.args[0]
				self.warning = "OverflowError: " + text + " (fatal minimisation error)."
				break
			except NameError, message:
				self.warning = message.args[0] + " (fatal minimisation error)."
				break

			# Test for warnings.
			if self.warning != None:
				break

			# Maximum number of iteration test.
			if self.k >= self.maxiter:
				self.warning = "Maximum number of iterations reached"
				break

			# Convergence test.
			if self.conv_test(self.fk_new, self.fk, self.dfk_new):
				break

			# Update function.
			try:
				self.update()
			except OverflowError, message:
				if type(message.args[0]) == int:
					text = message.args[1]
				else:
					text = message.args[0]
				self.warning = "OverflowError: " + text + " (fatal minimisation error)."
				break
			except NameError, message:
				if type(message.args[0]) == int:
					self.warning = message.args[1]
				else:
					self.warning = message.args[0]
				break

			# Iteration counter update.
			self.k = self.k + 1
			if self.print_flag:
				self.k2 = self.k2 + 1

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


	def setup(self):
		"""Default base class setup function.

		This function does nothing.
		"""

		pass


	def setup_conv_tests(self):
		"""Default base class for selecting the convergence tests.

		"""

		if self.func_tol and self.grad_tol:
			self.conv_test = self.double_test
		elif self.func_tol:
			self.conv_test = self.func_test
		elif self.grad_tol:
			self.conv_test = self.grad_test
		else:
			print self.print_prefix + "Convergence tests cannot be setup because both func_tol and grad_tol are set to None."
			self.init_failure = 1
			return


	def update(self):
		"""Default base class update function.

		xk+1 is shifted to xk
		fk+1 is shifted to fk
		"""

		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new





# The base class containing the generic line search functions.
##############################################################

class Line_search:
	def __init__(self):
		"Base class containing the generic line search functions."


	def backline(self):
		"Function for running the backtracking line search."

		self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
		self.f_count = self.f_count + fc


	def line_search_options(self, min_options):
		"""Line search options.

		Function for sorting out the minimisation options when the only option can be a line
		search.
		"""

		# Initialise.
		self.line_search_algor = None

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print self.print_prefix + "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1
			return

		# No more than one option is allowed.
		if len(min_options) > 1:
			print self.print_prefix + "A maximum of one minimisation options is allowed (the line search algorithm)."
			self.init_failure = 1
			return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.valid_line_search(opt):
				self.line_search_algor = opt
			else:
				print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid line search algorithm."
				self.init_failure = 1
				return

		# Default line search algorithm.
		if self.line_search_algor == None:
			self.line_search_algor = 'More Thuente'


	def mt(self):
		"Function for running the Mor� and Thuente line search."

		self.alpha, fc, gc = more_thuente(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc


	def no_search(self):
		"Set alpha to alpha0."

		self.alpha = self.a0


	def nwi(self):
		"Function for running the Nocedal and Wright interpolation based line search."

		self.alpha, fc = nocedal_wright_interpol(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, print_flag=0)
		self.f_count = self.f_count + fc


	def nww(self):
		"Function for running the Nocedal and Wright line search for the Wolfe conditions."

		self.alpha, fc, gc = nocedal_wright_wolfe(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc


	def setup_line_search(self):
		"The line search function."

		if match('^[Bb]ack', self.line_search_algor):
			if self.print_flag:
				print self.print_prefix + "Line search:  Backtracking line search."
			self.line_search = self.backline
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor) or match('^[Nn][Ww][Ii]', self.line_search_algor):
			if self.print_flag:
				print self.print_prefix + "Line search:  Nocedal and Wright interpolation based line search."
			self.line_search = self.nwi
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor) or match('^[Nn][Ww][Ww]', self.line_search_algor):
			if self.print_flag:
				print self.print_prefix + "Line search:  Nocedal and Wright line search for the Wolfe conditions."
			self.line_search = self.nww
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor) or match('^[Mm][Tt]', self.line_search_algor):
			if self.print_flag:
				print self.print_prefix + "Line search:  Mor� and Thuente line search."
			self.line_search = self.mt
		elif match('^[Nn]one$', self.line_search_algor):
			if self.print_flag:
				print self.print_prefix + "Line search:  No line search."
			self.line_search = self.no_search


	def valid_line_search(self, type):
		"Test if the string 'type' is a valid line search algorithm."

		if match('^[Bb]ack', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', type) or match('^[Nn][Ww][Ii]', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', type) or match('^[Nn][Ww][Ww]', type) or match('^[Mm]ore[ _][Tt]huente$', type) or match('^[Mm][Tt]', type) or match('^[Nn]one$', type):
			return 1
		else:
			return 0





# The base class containing the generic trust-region functions.
###############################################################

class Trust_region:
	def __init__(self):
		"Base class containing the generic trust-region functions."


	def trust_region_update(self):
		"""An algorithm for trust region radius selection.

		Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999,
		2nd ed.

		First calculate rho using the formula:

			        f(xk) - f(xk + pk)
			rho  =  ------------------
			          mk(0) - mk(pk)

		Where the numerator is called the actual reduction and the denominator is the predicted reduction.

		Secondly choose the trust region radius for the next iteration.
		Finally decide if xk+1 should be shifted to xk.
		"""

		# Actual reduction.
		act_red = self.fk - self.fk_new

		# Predicted reduction.
		pred_red = - dot(self.dfk, self.pk) - 0.5 * dot(self.pk, dot(self.d2fk, self.pk))

		# Rho.
		if pred_red == 0.0:
			self.rho = 1e99
		else:
			self.rho = act_red / pred_red

		# Calculate the Euclidean norm of pk.
		self.norm_pk = sqrt(dot(self.pk, self.pk))

		if self.print_flag >= 2:
			print self.print_prefix + "Actual reduction: " + `act_red`
			print self.print_prefix + "Predicted reduction: " + `pred_red`
			print self.print_prefix + "rho: " + `self.rho`
			print self.print_prefix + "||pk||: " + `self.norm_pk`

		# Rho is close to zero or negative, therefore the trust region is shrunk.
		if self.rho < 0.25 or pred_red < 0.0:
			self.delta = 0.25 * self.delta
			if self.print_flag >= 2:
				print self.print_prefix + "Shrinking the trust region."

		# Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
		elif self.rho > 0.75 and abs(self.norm_pk - self.delta) < 1e-5:
			self.delta = min(2.0*self.delta, self.delta_max)
			if self.print_flag >= 2:
				print self.print_prefix + "Expanding the trust region."

		# Rho is positive but not close to one, therefore the trust region is unaltered.
		else:
			if self.print_flag >= 2:
				print self.print_prefix + "Trust region is unaltered."

		if self.print_flag >= 2:
			print self.print_prefix + "New trust region: " + `self.delta`

		# Choose the position for the next iteration.
		if self.rho > self.eta and pred_red > 0.0:
			self.shift_flag = 1
			if self.print_flag >= 2:
				print self.print_prefix + "rho > eta, " + `self.rho` + " > " + `self.eta`
				print self.print_prefix + "Moving to, self.xk_new: " + `self.xk_new`
		else:
			self.shift_flag = 0
			if self.print_flag >= 2:
				print self.print_prefix + "rho < eta, " + `self.rho` + " < " + `self.eta`
				print self.print_prefix + "Not moving, self.xk: " + `self.xk`





# The base class containing the generic conjugate gradient functions.
#####################################################################

class Conjugate_gradient:
	def __init__(self):
		"Class containing the non-specific conjugate gradient code."


	def new_param_func(self):
		"""The new parameter function.

		Do a line search then calculate xk+1, fk+1, and gk+1.
		"""

		# Line search.
		self.line_search()

		# Find the new parameter vector and function value at that point.
		self.xk_new = self.xk + self.alpha * self.pk
		self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
		self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

		if self.print_flag >= 2:
			print self.print_prefix + "New param func:"
			print self.print_prefix + "\ta:    " + `self.alpha`
			print self.print_prefix + "\tpk:   " + `self.pk`
			print self.print_prefix + "\txk:   " + `self.xk`
			print self.print_prefix + "\txk+1: " + `self.xk_new`
			print self.print_prefix + "\tfk:   " + `self.fk`
			print self.print_prefix + "\tfk+1: " + `self.fk_new`
			print self.print_prefix + "\tgk:   " + `self.dfk`
			print self.print_prefix + "\tgk+1: " + `self.dfk_new`


	def setup(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and Hessian matrix are
		calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.pk = -self.dfk
		self.dot_dfk = dot(self.dfk, self.dfk)


	def old_cg_conv_test(self):
		"""Convergence tests.

		This is old code implementing the conjugate gradient convergence test given on page
		124 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd
		ed.  This function is currently unused.
		"""

		inf_norm = 0.0
		for i in range(len(self.dfk)):
			inf_norm = max(inf_norm, abs(self.dfk[i]))
		if inf_norm < self.grad_tol * (1.0 + abs(self.fk)):
			return 1
		elif self.fk_new - self.fk == 0.0:
			self.warning = "Function tol of zero reached."
			return 1


	def update(self):
		"Function to update the function value, gradient vector, and Hessian matrix"

		# Gradient dot product at k+1.
		self.dot_dfk_new = dot(self.dfk_new, self.dfk_new)

		# Calculate beta at k+1.
		bk_new = self.calc_bk()

		# Restarts.
		if abs(dot(self.dfk_new, self.dfk)) / self.dot_dfk_new >= 0.1:
			if self.print_flag >= 2:
				print self.print_prefix + "Restarting."
			bk_new = 0

		# Calculate pk+1.
		self.pk_new = -self.dfk_new + bk_new * self.pk

		if self.print_flag >= 2:
			print self.print_prefix + "Update func:"
			print self.print_prefix + "\tpk:     " + `self.pk`
			print self.print_prefix + "\tpk+1:   " + `self.pk_new`

		# Update.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk = self.dfk_new * 1.0
		self.pk = self.pk_new * 1.0
		self.dot_dfk = self.dot_dfk_new
