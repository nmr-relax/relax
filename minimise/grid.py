import sys
from Numeric import Float64, ones, copy, zeros
from re import match

class grid:
	def __init__(self, mf):
		"Grid search."
		self.mf = mf


	def search(self, function, fargs=(), args=[[]]):
		"""Grid search function.

		Function arguments
		~~~~~~~~~~~~~~~~~~

		1:  function - the function to minimise which should return a single value.
		2:  fargs - tuple.  The function options.
		3:  args - matrix.  Options for the grid search with the first dimension correponding to the parameters of
		the grid, and the second has the following elements:
			0 - The number of increments.
			1 - Lower limit.
			2 - Upper limit.


		Returned by the function
		~~~~~~~~~~~~~~~~~~~~~~~~

		1:  An array with the parameter values at the minimum chi-squared value.
		2:  The minimum chi-squared value.

		"""

		self.grid_options = args

		# Initialise data structures.
		self.num_params = len(self.grid_options)
		total_steps = 1.0
		self.step_num = ones((self.num_params))
		self.step_size = zeros((self.num_params), Float64)
		self.params = zeros((self.num_params), Float64)
		self.min_params = zeros((self.num_params), Float64)
		for k in range(self.num_params):
			self.step_size[k] = (self.grid_options[k][2] - self.grid_options[k][1]) / (self.grid_options[k][0] - 1)
			self.params[k] = self.grid_options[k][1]
			self.min_params[k] = self.grid_options[k][1]
			total_steps = total_steps * self.grid_options[k][0]

		# Back calculate the initial function values and the chi-squared statistic.
		self.chi2 = apply(function, (self.params,)+fargs)
		self.min_chi2 = self.chi2

		# Debugging code.
		if self.mf.min_debug >= 1:
			print "%-20s%-20i" % ("Total_steps:", total_steps)
			if self.mf.min_debug == 2:
				print "%-20s%-20s\n" % ("Step size:", `self.step_size`)
			print "%-6s%-8i%-12s%-20s" % ("Step:", 1, "Min params:", `self.params`)
			if self.mf.min_debug == 2:
				print "%-20s%-20i" % ("Step number:", 1)
				print "%-20s%-20s" % ("Increment:", `self.step_num`)
				print "%-20s%-20s" % ("Init params:", `self.params`)
				print "%-20s%-20g\n" % ("Init chi2:", self.chi2)

		# Grid search.
		for step in range(2, total_steps + 1):
			# Loop over the parameters.
			for k in range(self.num_params):
				if self.step_num[k] < self.grid_options[k][0]:
					self.step_num[k] = self.step_num[k] + 1
					self.params[k] = self.params[k] + self.step_size[k]
					# Exit so that the other step numbers are not incremented.
					break
				else:
					self.step_num[k] = 1
					self.params[k] = self.grid_options[k][1]

			# Back calculate the initial function values and the chi-squared statistic.
			self.chi2 = apply(function, (self.params,)+fargs)

			# Test if the chi-squared value is less than the least chi-squared value.
			if self.chi2 < self.min_chi2:
				self.min_chi2 = self.chi2
				self.min_params = copy.deepcopy(self.params)

				# Debugging code.
				if self.mf.min_debug >= 1:
					print "%-6s%-8i%-12s%-65s%-6s%-20s" % ("Step:", step, "Min params:", `self.min_params`, "Chi2:", `self.min_chi2`)

			# Debugging code.
			if self.mf.min_debug == 2:
				print "%-20s%-20i" % ("Step number:", step)
				print "%-20s%-20s" % ("Increment:", `self.step_num`)
				print "%-20s%-20s" % ("Params:", `self.params`)
				print "%-20s%-20g" % ("Chi2:", self.chi2)
				print "%-20s%-20s" % ("Min params:", `self.min_params`)
				print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

		return self.min_params, self.min_chi2
