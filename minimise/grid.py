import sys
from re import match

class grid:
	def __init__(self, mf):
		"Grid search."
		self.mf = mf


	def search(self, function, function_options, chi2_func, grid_options, values, data_points, errors):
		"""Levenberg-Marquardt minimisation function.

		'function' is the function to minimise, and should return a single value.
		'function_options' are the function options to pass to 'function' and 'dfunction'.
		'values' is an array containing the values to minimise on, eg peak heights or relaxation rates.
		'data_points' is an array containing information on type corresponding to 'values', eg relaxation time or relaxation data type.
		'errors' is an array containing the errors associated with 'values'
		'start_params' is the starting parameter values.

		The following are returned:
			1. An array with the parameter values at the chi-squared minimum.
			2. The minimum chi-squared value.


		"""

		self.function = function
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.grid_options = grid_options
		self.values = values
		self.data_points = data_points
		self.errors = errors

		# Initialise data structures.
		self.num_params = len(grid_options)
		total_steps = 1.0
		self.step_size = []
		self.step_num = []
		self.params = []
		self.min_params = []
		for param in range(len(grid_options)):
			step = (self.grid_options[param][2] - self.grid_options[param][1]) / (self.grid_options[param][0] - 1)
			self.step_size.append(step)
			self.step_num.append(1)
			self.params.append(self.grid_options[param][1])
			self.min_params.append(self.grid_options[param][1])
			total_steps = total_steps * self.grid_options[param][0]

		# Back calculate the initial function values and the chi-squared statistic.
		self.back_calc = []
		for i in range(len(self.data_points)):
			self.back_calc.append(function(self.function_options, self.data_points[i], self.params))
		self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)
		self.min_chi2 = self.chi2

		if self.mf.min_debug >= 1:
			print "%-20s%-20i" % ("Total_steps:", total_steps)
		if self.mf.min_debug == 2:
			print "%-20s%-20s" % ("Step size:", `self.step_size`)
			print "%-20s%-20s" % ("Init step num:", `self.step_num`)
			print "%-20s%-20s" % ("Init params:", `self.params`)
			print "%-20s%-20g\n" % ("Init chi2:", self.chi2)

		for step in range(1, total_steps - 1):
			# Loop over the parameters.
			for param in range(len(grid_options)):
				if self.step_num[param] < self.grid_options[param][0]:
					self.step_num[param] += 1
					self.params[param] = self.params[param] + self.step_size[param]
					break
				else:
					self.step_num[param] = 1
					self.params[param] = self.grid_options[param][1]
	
			# Back calculate the initial function values and the chi-squared statistic.
			self.back_calc = []
			for i in range(len(self.data_points)):
				self.back_calc.append(function(self.function_options, self.data_points[i], self.params))
			self.chi2 = self.chi2_func(self.values, self.back_calc, self.errors)
	
			if self.chi2 < self.min_chi2:
				self.min_chi2 = self.chi2
				for param in range(len(grid_options)):
					self.min_params[param] = self.params[param]
				if self.mf.min_debug >= 1:
					print "%-6s%-8i%-12s%-20s" % ("Step:", step, "Min params:", `self.min_params`)

			if self.mf.min_debug == 2:
				print "%-20s%-20i" % ("Step number:", step)
				print "%-20s%-20s" % ("Step num:", `self.step_num`)
				print "%-20s%-20s" % ("Params:", `self.params`)
				print "%-20s%-20g" % ("Chi2:", self.chi2)
				print "%-20s%-20s" % ("Min params:", `self.min_params`)
				print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

		return self.min_params, self.min_chi2
