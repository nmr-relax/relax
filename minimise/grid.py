import sys
from re import match

class grid:
	def __init__(self, mf):
		"Grid search."
		self.mf = mf


	def search(self, function, function_options, chi2_func, values, errors, grid_options):
		"""Levenberg-Marquardt minimisation function.

		'function' is the function to minimise, and should return a single value.
		'function_options' are the function options to pass to 'function'.
		'values' is an array containing the values, eg peak heights or relaxation rates.
		'errors' is an array containing the errors associated with 'values'
		'grid_options' is an array of arrays of options for the grid search with the first dimension
		correponding to the parameters of the grid, and the second has the following elements:
			0 - The number of increments.
			1 - Lower limit.
			2 - Upper limit.

		The following are returned:
			1. An array with the parameter values with the minimum chi-squared value.
			2. The minimum chi-squared value.
		"""

		self.function = function
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.values = values
		self.errors = errors
		self.grid_options = grid_options

		# Initialise data structures.
		self.num_params = len(grid_options)
		total_steps = 1.0
		self.step_size = []
		self.step_num = []
		self.params = []
		self.min_params = []
		for k in range(self.num_params):
			step = (self.grid_options[k][2] - self.grid_options[k][1]) / (self.grid_options[k][0] - 1)
			self.step_size.append(step)
			self.step_num.append(1)
			self.params.append(self.grid_options[k][1])
			self.min_params.append(self.grid_options[k][1])
			total_steps = total_steps * self.grid_options[k][0]

		# Back calculate the initial function values and the chi-squared statistic.
		self.back_calc = function(self.function_options, self.params)
		self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)
		self.min_chi2 = self.chi2

		if self.mf.min_debug >= 1:
			print "%-20s%-20i" % ("Total_steps:", total_steps)
		if self.mf.min_debug == 2:
			print "%-20s%-20s\n" % ("Step size:", `self.step_size`)
		if self.mf.min_debug >= 1:
			print "%-6s%-8i%-12s%-20s" % ("Step:", 1, "Min params:", `self.params`)
		if self.mf.min_debug == 2:
			print "%-20s%-20i" % ("Step number:", 1)
			print "%-20s%-20s" % ("Increment:", `self.step_num`)
			print "%-20s%-20s" % ("Init params:", `self.params`)
			print "%-20s%-20g\n" % ("Init chi2:", self.chi2)

		for step in range(2, total_steps - 1):
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
			self.back_calc = function(self.function_options, self.params)
			self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)
	
			if self.chi2 < self.min_chi2:
				self.min_chi2 = self.chi2
				self.min_params = self.params[:]
				if self.mf.min_debug >= 1:
					print "%-6s%-8i%-12s%-20s" % ("Step:", step, "Min params:", `self.min_params`)

			if self.mf.min_debug == 2:
				print "%-20s%-20i" % ("Step number:", step)
				print "%-20s%-20s" % ("Increment:", `self.step_num`)
				print "%-20s%-20s" % ("Params:", `self.params`)
				print "%-20s%-20g" % ("Chi2:", self.chi2)
				print "%-20s%-20s" % ("Min params:", `self.min_params`)
				print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

		return self.min_params, self.min_chi2
