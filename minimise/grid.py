import sys
from re import match

class grid:
	def __init__(self, mf):
		"Grid search."
		self.mf = mf


	def search(self, function, function_options, derivative_flag, chi2_func, values, errors, grid_options):
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
		self.derivative_flag = derivative_flag
		self.chi2_func = chi2_func
		self.values = values
		self.errors = errors
		self.grid_options = grid_options

		# Initialise data structures.
		#self.num_params = len(grid_options)
		#total_steps = 1.0
		#self.step_size = []
		#self.step_num = []
		#self.params = []
		#self.min_params = []
		#for k in range(self.num_params):
		#	step = (self.grid_options[k][2] - self.grid_options[k][1]) / (self.grid_options[k][0] - 1)
		#	self.step_size.append(step)
		#	self.step_num.append(1)
		#	self.params.append(self.grid_options[k][1])
		#	self.min_params.append(self.grid_options[k][1])
		#	total_steps = total_steps * self.grid_options[k][0]

		# Back calculate the initial function values and the chi-squared statistic.
		#self.chi2 = self.chi2_func(self.values, function(self.function_options, self.derivative_flag, self.params), self.errors)
		#self.min_chi2 = self.chi2

		#if self.mf.min_debug >= 1:
		#	print "%-20s%-20i" % ("Total_steps:", total_steps)
		#	if self.mf.min_debug == 2:
		#		print "%-20s%-20s\n" % ("Step size:", `self.step_size`)
		#	print "%-6s%-8i%-12s%-20s" % ("Step:", 1, "Min params:", `self.params`)
		#	if self.mf.min_debug == 2:
		#		print "%-20s%-20i" % ("Step number:", 1)
		#		print "%-20s%-20s" % ("Increment:", `self.step_num`)
		#		print "%-20s%-20s" % ("Init params:", `self.params`)
		#		print "%-20s%-20g\n" % ("Init chi2:", self.chi2)

		if len(grid_options) == 1:
			self.grid_1d()
		elif len(grid_options) == 2:
			self.grid_2d()
		elif len(grid_options) == 3:
			self.grid_3d()

		return self.min_params, self.min_chi2


	def grid_1d(self):
		self.params = [ self.grid_options[0][1] ]
		self.min_chi2 = 1e999
		self.min_params = self.params[:]
		inc_0 = (self.grid_options[0][2] - self.grid_options[0][1]) / (self.grid_options[0][0] - 1.0)

		for i in range(self.grid_options[0][0]):
			# Back calculate the initial function values and the chi-squared statistic.
			self.chi2 = self.chi2_func(self.values, self.function(self.function_options, self.derivative_flag, self.params), self.errors)

			if self.chi2 < self.min_chi2:
				self.min_chi2 = self.chi2
				self.min_params = self.params[:]
				if self.mf.min_debug >= 1:
					print "%-6s%-8i%-12s%-20s" % ("Step:", i+1, "Min params:", `self.min_params`)

			if self.mf.min_debug == 2:
				print "%-20s%-20i" % ("Step number:", i+1)
				#print "%-20s%-20s" % ("Increment:", `self.step_num`)
				print "%-20s%-20s" % ("Params:", `self.params`)
				print "%-20s%-20g" % ("Chi2:", self.chi2)
				print "%-20s%-20s" % ("Min params:", `self.min_params`)
				print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

			self.params[0] = self.params[0] + inc_0


	def grid_2d(self):
		self.params = [ self.grid_options[0][1], self.grid_options[1][1] ]
		self.min_chi2 = 1e999
		self.min_params = self.params[:]
		inc_0 = (self.grid_options[0][2] - self.grid_options[0][1]) / (self.grid_options[0][0] - 1.0)
		inc_1 = (self.grid_options[1][2] - self.grid_options[1][1]) / (self.grid_options[1][0] - 1.0)

		for j in range(self.grid_options[1][0]):
			for i in range(self.grid_options[0][0]):
				# Back calculate the initial function values and the chi-squared statistic.
				self.chi2 = self.chi2_func(self.values, self.function(self.function_options, self.derivative_flag, self.params), self.errors)

				if self.chi2 < self.min_chi2:
					self.min_chi2 = self.chi2
					self.min_params = self.params[:]
					if self.mf.min_debug >= 1:
						print "%-6s%-8i%-12s%-20s" % ("Step:", (j*self.grid_options[0][0]+i+1), "Min params:", `self.min_params`)

				if self.mf.min_debug == 2:
					print "%-20s%-20i" % ("Step number:", (j*self.grid_options[0][0]+i+1))
					#print "%-20s%-20s" % ("Increment:", `self.step_num`)
					print "%-20s%-20s" % ("Params:", `self.params`)
					print "%-20s%-20g" % ("Chi2:", self.chi2)
					print "%-20s%-20s" % ("Min params:", `self.min_params`)
					print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

				self.params[0] = self.params[0] + inc_0
			self.params[0] = self.grid_options[0][1]
			self.params[1] = self.params[1] + inc_1


	def grid_3d(self):
		self.params = [ self.grid_options[0][1], self.grid_options[1][1], self.grid_options[2][1] ]
		self.min_chi2 = 1e999
		self.min_params = self.params[:]
		inc_0 = (self.grid_options[0][2] - self.grid_options[0][1]) / (self.grid_options[0][0] - 1.0)
		inc_1 = (self.grid_options[1][2] - self.grid_options[1][1]) / (self.grid_options[1][0] - 1.0)
		inc_2 = (self.grid_options[2][2] - self.grid_options[2][1]) / (self.grid_options[2][0] - 1.0)

		for k in range(self.grid_options[2][0]):
			for j in range(self.grid_options[1][0]):
				for i in range(self.grid_options[0][0]):
					# Back calculate the initial function values and the chi-squared statistic.
					self.chi2 = self.chi2_func(self.values, self.function(self.function_options, self.derivative_flag, self.params), self.errors)

					if self.chi2 < self.min_chi2:
						self.min_chi2 = self.chi2
						self.min_params = self.params[:]
						if self.mf.min_debug >= 1:
							print "%-6s%-8i%-12s%-20s" % ("Step:", (k*self.grid_options[0][0]*self.grid_options[1][0]+j*self.grid_options[1][0]+i+1), "Min params:", `self.min_params`)

					if self.mf.min_debug == 2:
						print "%-20s%-20i" % ("Step number:", (k*self.grid_options[0][0]*self.grid_options[1][0]+j*self.grid_options[1][0]+i+1))
						#print "%-20s%-20s" % ("Increment:", `self.step_num`)
						print "%-20s%-20s" % ("Params:", `self.params`)
						print "%-20s%-20g" % ("Chi2:", self.chi2)
						print "%-20s%-20s" % ("Min params:", `self.min_params`)
						print "%-20s%-20g\n" % ("Min Chi2:", self.min_chi2)

					self.params[0] = self.params[0] + inc_0
				self.params[0] = self.grid_options[0][1]
				self.params[1] = self.params[1] + inc_1
			self.params[0] = self.grid_options[0][1]
			self.params[1] = self.grid_options[1][1]
			self.params[2] = self.params[2] + inc_2


