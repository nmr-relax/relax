from re import match


class generic_minimise:
	def __init__(self):
		"""Base class containing the main minimisation iterative loop algorithm.

		The algorithm is defined in the minimise function.
		Also supplied are generic setup, convergence tests, and update functions.
		"""


	def hessian_type_and_mod(self, min_options, default_type='Newton', default_mod='GMW'):
		"""Hessian type and modification options.

		Function for sorting out the minimisation options when either the hessian type or
		hessian modification can be selected.
		"""

		# Initialise.
		self.hessian_type = None
		self.hessian_mod = None
		self.init_failure = 0

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1; return

		# Test that no more thant 2 options are given.
		if len(min_options) > 2:
			print "A maximum of two minimisation options is allowed (the hessian type and hessian modification)."
			self.init_failure = 1; return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.hessian_type == None and (match('[Bb][Ff][Gg][Ss]', opt) or match('[Nn]ewton', opt)):
				self.hessian_type = opt
			elif self.hessian_mod == None and self.valid_hessian_mod(opt):
				self.hessian_mod = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid hessian type or modification."
				self.init_failure = 1; return

		# Default hessian type.
		if self.hessian_type == None:
			self.hessian_type = default_type

		# Make sure that no hessian modification is used with the BFGS matrix.
		if match('[Bb][Ff][Gg][Ss]', self.hessian_type) and self.hessian_mod != None:
			print "When using the BFGS matrix, hessian modifications should not be used."
			self.init_failure = 1; return

		# Default hessian modification when the hessian type is Newton.
		if match('[Nn]ewton', self.hessian_type) and self.hessian_mod == None:
			self.hessian_mod = default_mod

		# Print the hessian type info.
		if self.print_flag:
			if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
				print "Hessian type:  BFGS"
			else:
				print "Hessian type:  Newton"


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
			self.warning = "Function tol reached."
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
