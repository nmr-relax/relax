import sys


class simplex:
	def __init__(self, mf):
		"Simplex minimisation class."
		self.mf = mf


	def fit(self, function, function_options, chi2_func, values, errors, init_simplex):
		"""Downhill simplex minimisation function.

		"""

		self.function = function
		self.function_options = function_options
		self.chi2_func = chi2_func
		self.values = values
		self.errors = errors
		self.simplex = init_simplex

		if match('m1', self.mf.data.model):
			print "One dimensional simplex minimisation, quitting program!"
		factor = 1.0
		num_runs = 0.0
		for i in range(10):
			self.simplex = self.create_simplex(params, grid_ops, factor)
			if self.mf.min_debug >= 1:
				print "\nThe initial simplex is: " + `self.simplex`

			# Create the initial chi-squared vector.
			self.chi2 = []
			for vertex in range(len(self.simplex)):
				self.chi2.append(self.chi2_func(self.values, function(self.function_options, self.simplex[vertex]), self.errors))

			# Print debugging info
			if self.mf.min_debug == 2:
				print "\n\n"
				print "%-29s%-40s" % ("Minimisation run number:", `0`)
				print "%-29s%-40s" % ("Initial simplex:", `self.simplex`)
				print "%-29s%-40s" % ("Initial chi2 vector:", `self.chi2`)
			minimise_num = 1

			# Iterate until the minimiser is finished.
			while 1:
				# Print debugging info
				if self.mf.min_debug == 2:
					print "\n\n"
					print "%-29s%-40s" % ("Minimisation run number:", `minimise_num`)
					print "%-29s%-40s" % ("Simplex:", `self.simplex`)
					print "%-29s%-40s" % ("Chi-squared vector:", `self.chi2`)

				# Find the simplex point with the lowest chi-squared value.
				index_high = 0
				index_2nd_high = 0
				index_low = 0
				if self.chi2[1] > self.chi2[0]:
					index_high = 1
				else:
					index_low = 1
				if len(self.simplex) > 2:
					for vertex in range(2, len(self.simplex)):
						if self.chi2[vertex] > self.chi2[index_high]:
							index_2nd_high = index_high
							index_high = vertex
						if self.chi2[vertex] < self.chi2[index_low]:
							index_low = vertex
				if self.mf.min_debug == 2:
					print "%-29s%-40s" % ("Index high:", `index_high`)
					print "%-29s%-40s" % ("Index 2nd high:", `index_2nd_high`)
					print "%-29s%-40s" % ("Index low:", `index_low`)

				# Finish minimising when the chi-squared difference is insignificant.
				if self.chi2[index_high] - self.chi2[index_low] < 1e-10:
					if self.mf.min_debug == 2:
						print "\n%-29s%-40e" % ("Chi-squared diff:", self.chi2[index_high] - self.chi2[index_low])
						print "%-29s%-40e" % ("Chi-squared diff limit:", 1e-10)
						print "Insignificant chi2 difference, stopped minimising."
					break

				# Calculate the vector for the center of the simplex.
				self.ave_vector = []
				for param in range(len(self.simplex[0])):
					ave = 0.0
					for point in range(len(self.simplex)):
						ave = ave + self.simplex[point][param]
					ave = ave / float(len(self.simplex))
					self.ave_vector.append(ave)
				if self.mf.min_debug == 2:
					print "%-29s%-40s" % ("Ave vector:", `self.ave_vector`)

				# Preserve copies of the simplex and chi-squared vector.
				self.new_simplex = []
				for vertex in range(len(self.simplex)):
					self.new_simplex.append(self.simplex[vertex][:])
				self.new_chi2 = self.chi2[:]


				# Reflection.
				#############
				reflection_vector = self.move(self.simplex[index_high], 1.0)
				reflection_chi2 = self.chi2_func(self.values, function(self.function_options, reflection_vector), self.errors)
				if self.mf.min_debug == 2:
					print "%-29s%-40s" % ("Reflection vector:", `reflection_vector`)
					print "%-29s%-40s" % ("Reflection chi2:", `reflection_chi2`)

				# Update simplex with the reflection vector.
				if reflection_chi2 < self.chi2[index_high]:
					self.new_simplex[index_high] = reflection_vector[:]
					self.new_chi2[index_high] = reflection_chi2


				# Extension.
				############
				if reflection_chi2 <= self.chi2[index_low]:
					extension_vector = self.move(self.simplex[index_high], 2.0)
					extension_chi2 = self.chi2_func(self.values, function(self.function_options, extension_vector), self.errors)
					if self.mf.min_debug == 2:
						print "%-29s%-40s" % ("Extension vector:", `extension_vector`)
						print "%-29s%-40s" % ("Extension chi2:", `extension_chi2`)

					# Update simplex with the extension vector.
					if extension_chi2 <= self.chi2[index_high]:
						self.new_simplex[index_high] = extension_vector[:]
						self.new_chi2[index_high] = extension_chi2


				# Contraction.
				##############
				elif reflection_chi2 >= self.chi2[index_2nd_high]:
					contract_vector = self.move(self.simplex[index_high], -0.5)
					contract_chi2 = self.chi2_func(self.values, function(self.function_options, contract_vector), self.errors)
					if self.mf.min_debug == 2:
						print "%-29s%-40s" % ("Contraction vector:", `contract_vector`)
						print "%-29s%-40s" % ("Contraction chi2:", `contract_chi2`)

					# Update simplex with the contraction vector.
					if contract_chi2 <= self.chi2[index_high]:
						self.new_simplex[index_high] = contract_vector[:]
						self.new_chi2[index_high] = contract_chi2


					# Shrink.
					#########
					# This code has not been debugged!!!
					if contract_chi2 >= self.chi2[index_high]:
						# Loop over the vertices.
						for vertex in range(len(self.simplex)):
							if vertex == index_low:
								continue
							shrink_vector = []
							# Loop over the parameters.
							for param in range(len(self.simplex[0])):
								new_param = 0.5 * self.simplex[index_low][param] + self.simplex[vertex][param]
								shrink_vector.append(new_param)
							self.new_simplex[vertex] = shrink_vector[:]
						if self.mf.min_debug == 2:
							print "Shrinking"
							print "\t%-29s%-40s" % ("Old simplex:", `self.simplex`)
							print "\t%-29s%-40s" % ("New simplex:", `self.new_simplex`)


				# Update the simplex and chi-squared vector.
				for vertex in range(len(self.simplex)):
					self.simplex[vertex] = self.new_simplex[vertex][:]
				self.chi2 = self.new_chi2[:]

				# Print debugging info
				if self.mf.min_debug == 2:
					print "%-29s%-40s" % ("New simplex:", `self.simplex`)
					print "%-29s%-40s" % ("New chi-squared vector:", `self.chi2`)

				minimise_num = minimise_num + 1

			if self.mf.min_debug >= 1:
				print "The final simplex is: " + `self.simplex`
				print "The final chi2 vector is: " + `self.chi2`

			factor = factor / 10.0
			num_runs = num_runs + runs

		print "\n\nTotal number of runs: " + `num_runs`

		return self.simplex[index_low], self.chi2[index_low], minimise_num


	def create_simplex(self, params, grid_ops, factor):
		"""Function to create the initial simplex.

		params will become the first point of the simplex.
		grid_ops is used to create the other points of the simplex.
		"""
		simplex = []
		simplex.append(params)
		for i in range(len(params)):
			delta = factor * (grid_ops[i][2] - grid_ops[i][1]) / (grid_ops[i][0] - 1)
			new_point = []
			for j in range(len(params)):
				if i == j:
					new_point.append(params[j] + delta)
				else:
					new_point.append(params[j])
			simplex.append(new_point)
		return simplex


	def move(self, vertex, factor):
		"Function to do something?"

		# Calculate the new vector.
		new_vector = []
		for param in range(len(self.simplex[0])):
			new = self.ave_vector[param] * (1 + factor) - factor * vertex[param]
			new_vector.append(new)

		return new_vector

