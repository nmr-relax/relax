from Numeric import copy


class generic_minimise:
	def __init__(self):
		"""Generic code for iterative minimisers.


		Function options
		~~~~~~~~~~~~~~~~

		func			- The function to minimise.
		dfunc			- The function which returns the gradient vector.
		d2func			- The function which returns the hessian matrix or approximation.

		f_args			- The tuple of arguments to supply to the function func.
		df_args			- The tuple of arguments to supply to the function dfunc.
		d2f_args		- The tuple of arguments to supply to the function d2func.

		xk			- The parameter vector which on input is the initial values, x0.
		fk			- The function value which on input corresponds to x0.
		dfk			- The gradient vector which on input corresponds to x0.
		d2fk			- The hessian matrix or approximation which on input corresponds to x0.

		xk_new			- The parameter vector for the next iteration which on input can be anything.
		fk_new			- The function value for the next iteration which on input can be anything.
		dfk_new			- The gradient vector for the next iteration which on input can be anything.
		d2fk_new		- The hessian matrix for the next iteration which on input can be anything.

		func_tol		- The cutoff value used to terminate minimisation by comparison to the difference in function values between iterations.
		maxiter			- The maximum number of iterations.
		print_flag		- A flag specifying how much information should be printed to standard output during minimisation:

		The print flag corresponds to:
			0 - No output.
			1 - Minimal output.
			2 - Full output.


		Returned objects
		~~~~~~~~~~~~~~~~

		The minimised parameter vector, function value at the minimum, number of iterations, and a warning flag are returned.
		The warning flag corresponds to:
			0 - Minimisation terminated successfully.
			1 - Maximum number of iterations have been reached.
		"""


	def generic_minimise(self):
		"""Generic code for iterative minimisers.

		"""

		# Start the iteration counter.
		self.k = 1

		# Debugging code.
		if self.print_flag:
			print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)
			self.k2 = 1

		# Iterate until the local minima is found.
		while 1:
			if self.print_flag == 2:
				print "\n\n<<<Main iteration k=" + `self.k` + " >>>"

			# Debugging code.
			if self.print_flag:
				if self.print_flag == 2:
					print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)
				else:
					if self.k2 == 101:
						print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", self.k, "Min params:", `self.xk`, "Function value:", `self.fk`)
						self.k2 = 1

			# Find the new parameter vector self.xk_new.
			self.xk_new = self.new_param_func()

			# Make a backup of the current data.
			self.fk_last = self.fk
			try:
				self.backup_current_data()
			except AttributeError:
				"Don't backup the current data."

			# Find the parameter vector, function value, gradient vector, and hessian matrix for iteration k+1.
			self.xk = copy.deepcopy(self.xk_new)
			self.update_data()

			# Test if maximum number of iterations have been reached.
			if self.k >= self.maxiter:
				self.warning = "Maximum number of iterations reached"
				break

			# Tests.
			finished = self.tests()
			if finished:
				break

			# Update data for the next iteration.
			self.k = self.k + 1

			# Debugging code.
			if self.print_flag:
				self.k2 = self.k2 + 1


	def init_data(self):
		"Generic data initialisation."

		self.func = self.min_args[0]
		self.dfunc = self.min_args[1]
		self.d2func = self.min_args[2]
		self.args = self.min_args[3]
		self.xk = self.min_args[4]
		self.minimiser = self.min_args[5]
		self.func_tol = self.min_args[6]
		self.maxiter = self.min_args[7]
		self.full_output = self.min_args[8]
		self.print_flag = self.min_args[9]

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None


	def tests(self):
		"Test for the local minimum."

		if abs(self.fk_last - self.fk) <= self.func_tol:
			return 1
		else:
			return 0
