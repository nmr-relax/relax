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

def minimise(func, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0):
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
	| Polak-Ribière                     | '^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'         |
	| Polak-Ribière +                   | '^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'     |
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
		if print_flag:
			print "\n\n<<< Grid search >>>"
		xk, fk, k = grid(func, args=args, grid_ops=min_options, print_flag=print_flag)
		if full_output:
			results = (xk, fk, k, k, 0, 0, None)
		else:
			results = xk

	# Fixed parameter values.
	elif match('^[Ff]ixed', min_algor):
		if print_flag:
			print "\n\n<<< Fixed initial parameter values >>>"
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
		if print_flag:
			print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
		results = coordinate_descent(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Steepest descent minimisation.
	elif match('^[Ss][Dd]$', min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', min_algor):
		from minimise.steepest_descent import steepest_descent
		if print_flag:
			print "\n\n<<< Steepest descent minimisation >>>"
		results = steepest_descent(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Quasi-Newton BFGS minimisation.
	elif match('^[Bb][Ff][Gg][Ss]$', min_algor):
		from minimise.bfgs import bfgs
		if print_flag:
			print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
		results = bfgs(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Newton minimisation.
	elif match('^[Nn]ewton$', min_algor):
		from minimise.newton import newton
		if print_flag:
			print "\n\n<<< Newton minimisation >>>"
		results = newton(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Newton-CG minimisation.
	elif match('^[Nn]ewton[ _-][Cc][Gg]$', min_algor) or match('^[Nn][Cc][Gg]$', min_algor):
		from minimise.ncg import ncg
		if print_flag:
			print "\n\n<<< Newton Conjugate Gradient minimisation >>>"
		results = ncg(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Unconstrained trust-region algorithms.
	########################################

	# Cauchy point minimisation.
	elif match('^[Cc]auchy', min_algor):
		from minimise.cauchy_point import cauchy_point
		if print_flag:
			print "\n\n<<< Cauchy point minimisation >>>"
		results = cauchy_point(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Dogleg minimisation.
	elif match('^[Dd]ogleg', min_algor):
		from minimise.dogleg import dogleg
		if print_flag:
			print "\n\n<<< Dogleg minimisation >>>"
		results = dogleg(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# CG-Steihaug minimisation.
	elif match('^[Cc][Gg][-_ ][Ss]teihaug', min_algor) or match('^[Ss]teihaug', min_algor):
		from minimise.steihaug_cg import steihaug
		if print_flag:
			print "\n\n<<< CG-Steihaug minimisation >>>"
		results = steihaug(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Exact trust region minimisation.
	elif match('^[Ee]xact', min_algor):
		from minimise.exact_trust_region import exact_trust_region
		if print_flag:
			print "\n\n<<< Exact trust region minimisation >>>"
		results = exact_trust_region(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Unconstrained conjugate gradient algorithms.
	##############################################

	# Fletcher-Reeves conjugate gradient minimisation.
	elif match('^[Ff][Rr]$', min_algor) or match('^[Ff]letcher[-_ ][Rr]eeves$', min_algor):
		from minimise.fletcher_reeves_cg import fletcher_reeves
		if print_flag:
			print "\n\n<<< Fletcher-Reeves conjugate gradient minimisation >>>"
		results = fletcher_reeves(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Polak-Ribière conjugate gradient minimisation.
	elif match('^[Pp][Rr]$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere$', min_algor):
		from minimise.polak_ribiere_cg import polak_ribiere
		if print_flag:
			print "\n\n<<< Polak-Ribière conjugate gradient minimisation >>>"
		results = polak_ribiere(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Polak-Ribière + conjugate gradient minimisation.
	elif match('^[Pp][Rr]\+$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere\+$', min_algor):
		from minimise.polak_ribiere_plus_cg import polak_ribiere_plus
		if print_flag:
			print "\n\n<<< Polak-Ribière + conjugate gradient minimisation >>>"
		results = polak_ribiere_plus(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Hestenes-Stiefel conjugate gradient minimisation.
	elif match('^[Hh][Ss]$', min_algor) or match('^[Hh]estenes[-_ ][Ss]tiefel$', min_algor):
		from minimise.hestenes_stiefel_cg import hestenes_stiefel
		if print_flag:
			print "\n\n<<< Hestenes-Stiefel conjugate gradient minimisation >>>"
		results = hestenes_stiefel(func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Miscellaneous unconstrained algorithms.
	#########################################

	# Simplex minimisation.
	elif match('^[Ss]implex$', min_algor):
		from minimise.simplex import simplex
		if print_flag:
			print "\n\n<<< Simplex minimisation >>>"
		results = simplex(func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

	# Levenberg-Marquardt minimisation.
	elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
		from minimise.levenberg_marquardt import levenberg_marquardt
		if print_flag:
			print "\n\n<<< Levenberg-Marquardt minimisation >>>"
		results = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# Constrainted algorithms.
	##########################

	# Method of Multipliers.
	elif match('^[Mm][Oo][Mm]$', min_algor) or match('[Mm]ethod of [Mm]ultipliers$', min_algor):
		from minimise.method_of_multipliers import method_of_multipliers
		if print_flag:
			print "\n\n<<< Method of Multipliers >>>"
		results = method_of_multipliers(func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


	# No match to minimiser string.
	###############################

	else:
		print "Minimiser type set incorrectly.  The minimiser " + min_algor + " is not programmed.\n"
		return


	# Finish.
	#########

	if print_flag and results != None:
		if full_output:
			xk, fk, k, f_count, g_count, h_count, warning = results
			print "\nParameter values: " + `xk`
			print "Function value:   " + `fk`
			print "Iterations:       " + `k`
			print "Function calls:   " + `f_count`
			print "Gradient calls:   " + `g_count`
			print "Hessian calls:    " + `h_count`
			if warning:
				print "Warning:          " + warning
			else:
				print "Warning:          None"
		else:
			print "\nParameter values: " + `results`

	return results





# The generic minimisation base class (containing the main iterative loop).
###########################################################################

class Min:
	def __init__(self):
		"""Base class containing the main minimisation iterative loop algorithm.

		The algorithm is defined in the minimise function.
		Also supplied are generic setup, convergence tests, and update functions.
		"""


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
			print "The minimisation options " + `min_options` + " is not a tuple."
			return

		# Test that no more thant 2 options are given.
		if len(min_options) > 2:
			print "A maximum of two minimisation options is allowed (the Hessian type and Hessian modification)."
			return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.hessian_type == None and (match('[Bb][Ff][Gg][Ss]', opt) or match('[Nn]ewton', opt)):
				self.hessian_type = opt
			elif self.hessian_mod == None and self.valid_hessian_mod(opt):
				self.hessian_mod = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid Hessian type or modification."
				return

		# Default Hessian type.
		if self.hessian_type == None:
			self.hessian_type = default_type

		# Make sure that no Hessian modification is used with the BFGS matrix.
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type) and self.hessian_mod != None:
			print "When using the BFGS matrix, Hessian modifications should not be used."
			return

		# Default Hessian modification when the Hessian type is Newton.
		if match('[Nn]ewton', self.hessian_type) and self.hessian_mod == None:
			self.hessian_mod = default_mod

		# Print the Hessian type info.
		if self.print_flag:
			if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
				print "Hessian type:  BFGS"
			else:
				print "Hessian type:  Newton"

		return 1


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
				if self.print_flag == 2:
					print "\n\n<<<Main iteration k=" + `self.k` + " >>>"
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)
				else:
					if self.k2 == 100:
						self.k2 = 0
					if self.k2 == 0:
						print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)

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
			if self.tests():
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
			self.warning = None
			return 1
		else:
			if self.print_flag == 2:
				print "Pass function tol test."


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


	def init_line_functions(self):
		"The line search function."

		if match('^[Bb]ack', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Backtracking line search."
			self.line_search = self.backline
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor) or match('^[Nn][Ww][Ii]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright interpolation based line search."
			self.line_search = self.nwi
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor) or match('^[Nn][Ww][Ww]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright line search for the Wolfe conditions."
			self.line_search = self.nww
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor) or match('^[Mm][Tt]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Moré and Thuente line search."
			self.line_search = self.mt
		elif match('^[Nn]one$', self.line_search_algor):
			if self.print_flag:
				print "Line search:  No line search."
			self.line_search = self.no_search


	def line_search_option(self, min_options):
		"""Line search options.

		Function for sorting out the minimisation options when the only option can be a line
		search.
		"""

		# Initialise.
		self.line_search_algor = None

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print "The minimisation options " + `min_options` + " is not a tuple."
			return

		# No more than one option is allowed.
		if len(min_options) > 1:
			print "A maximum of one minimisation options is allowed (the line search algorithm)."
			return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.valid_line_search(opt):
				self.line_search_algor = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid line search algorithm."
				return

		# Default line search algorithm.
		if self.line_search_algor == None:
			self.line_search_algor = 'More Thuente'

		return 1


	def mt(self):
		"Function for running the Moré and Thuente line search."

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

		Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

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

		if self.print_flag == 2:
			print "Actual reduction: " + `act_red`
			print "Predicted reduction: " + `pred_red`
			print "rho: " + `self.rho`
			print "||pk||: " + `self.norm_pk`

		# Rho is close to zero or negative, therefore the trust region is shrunk.
		if self.rho < 0.25 or pred_red < 0.0:
			self.delta = 0.25 * self.delta
			if self.print_flag == 2:
				print "Shrinking the trust region."

		# Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
		elif self.rho > 0.75 and abs(self.norm_pk - self.delta) < 1e-5:
			self.delta = min(2.0*self.delta, self.delta_max)
			if self.print_flag == 2:
				print "Expanding the trust region."

		# Rho is positive but not close to one, therefore the trust region is unaltered.
		else:
			if self.print_flag == 2:
				print "Trust region is unaltered."

		if self.print_flag == 2:
			print "New trust region: " + `self.delta`

		# Choose the position for the next iteration.
		if self.rho > self.eta and pred_red > 0.0:
			self.shift_flag = 1
			if self.print_flag == 2:
				print "rho > eta, " + `self.rho` + " > " + `self.eta`
				print "Moving to, self.xk_new: " + `self.xk_new`
		else:
			self.shift_flag = 0
			if self.print_flag == 2:
				print "rho < eta, " + `self.rho` + " < " + `self.eta`
				print "Not moving, self.xk: " + `self.xk`





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

		if self.print_flag == 2:
			print "New param func:"
			print "\tLine search algor: " + self.line_search_algor
			print "\ta:    " + `self.alpha`
			print "\tpk:   " + `self.pk`
			print "\txk:   " + `self.xk`
			print "\txk+1: " + `self.xk_new`
			print "\tfk:   " + `self.fk`
			print "\tfk+1: " + `self.fk_new`
			print "\tgk:   " + `self.dfk`
			print "\tgk+1: " + `self.dfk_new`


	def setup(self):
		"""Setup function.

		The initial Newton function value, gradient vector, and Hessian matrix are calculated.
		"""

		self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
		self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
		self.pk = -self.dfk
		self.dot_dfk = dot(self.dfk, self.dfk)


	def tests(self):
		"Convergence tests."

		inf_norm = 0.0
		for i in range(len(self.dfk)):
			inf_norm = max(inf_norm, abs(self.dfk[i]))
		if inf_norm < 1e-10 * (1.0 + abs(self.fk)):
			self.warning = "Gradient tol reached."
			return 1
		elif abs(self.fk_new - self.fk) == 0.0:
			self.warning = "Function tol of zero reached."
			return 1
		else:
			return 0


	def update(self):
		"Function to update the function value, gradient vector, and Hessian matrix"

		# Gradient dot product at k+1.
		self.dot_dfk_new = dot(self.dfk_new, self.dfk_new)

		# Calculate beta at k+1.
		bk_new = self.calc_bk()

		# Restarts.
		if abs(dot(self.dfk_new, self.dfk)) / self.dot_dfk_new >= 0.1:
			if self.print_flag == 2:
				print "Restarting."
			bk_new = 0

		# Calculate pk+1.
		self.pk_new = -self.dfk_new + bk_new * self.pk

		if self.print_flag == 2:
			print "Update func:"
			print "\tpk:     " + `self.pk`
			print "\tpk+1:   " + `self.pk_new`

		# Update.
		self.xk = self.xk_new * 1.0
		self.fk = self.fk_new
		self.dfk = self.dfk_new * 1.0
		self.pk = self.pk_new * 1.0
		self.dot_dfk = self.dot_dfk_new
