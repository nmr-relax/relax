def simplex(function, function_options, chi2_func, values, errors, simplex, print_flag=0):
	"""Downhill simplex minimisation function.

	This code needs extensive modification to work properly!
	"""


	factor = 1.0
	num_runs = 0.0
	for i in range(10):
		simplex = create_simplex(params, grid_ops, factor)
		if print_flag >= 1:
			print "\nThe initial simplex is: " + `simplex`

		# Create the initial chi-squared vector.
		chi2 = []
		for vertex in range(len(simplex)):
			chi2.append(chi2_func(values, function(function_options, simplex[vertex]), errors))

		# Print debugging info
		if print_flag == 2:
			print "\n\n"
			print "%-29s%-40s" % ("Minimisation run number:", `0`)
			print "%-29s%-40s" % ("Initial simplex:", `simplex`)
			print "%-29s%-40s" % ("Initial chi2 vector:", `chi2`)
		minimise_num = 1

		# Iterate until the minimiser is finished.
		while 1:
			# Print debugging info
			if print_flag == 2:
				print "\n\n"
				print "%-29s%-40s" % ("Minimisation run number:", `minimise_num`)
				print "%-29s%-40s" % ("Simplex:", `simplex`)
				print "%-29s%-40s" % ("Chi-squared vector:", `chi2`)

			# Find the simplex point with the lowest chi-squared value.
			index_high = 0
			index_2nd_high = 0
			index_low = 0
			if chi2[1] > chi2[0]:
				index_high = 1
			else:
				index_low = 1
			if len(simplex) > 2:
				for vertex in range(2, len(simplex)):
					if chi2[vertex] > chi2[index_high]:
						index_2nd_high = index_high
						index_high = vertex
					if chi2[vertex] < chi2[index_low]:
						index_low = vertex
			if print_flag == 2:
				print "%-29s%-40s" % ("Index high:", `index_high`)
				print "%-29s%-40s" % ("Index 2nd high:", `index_2nd_high`)
				print "%-29s%-40s" % ("Index low:", `index_low`)

			# Finish minimising when the chi-squared difference is insignificant.
			if chi2[index_high] - chi2[index_low] < 1e-10:
				if print_flag == 2:
					print "\n%-29s%-40e" % ("Chi-squared diff:", chi2[index_high] - chi2[index_low])
					print "%-29s%-40e" % ("Chi-squared diff limit:", 1e-10)
					print "Insignificant chi2 difference, stopped minimising."
				break

			# Calculate the vector for the center of the simplex.
			ave_vector = []
			for param in range(len(simplex[0])):
				ave = 0.0
				for point in range(len(simplex)):
					ave = ave + simplex[point][param]
				ave = ave / float(len(simplex))
				ave_vector.append(ave)
			if print_flag == 2:
				print "%-29s%-40s" % ("Ave vector:", `ave_vector`)

			# Preserve copies of the simplex and chi-squared vector.
			new_simplex = []
			for vertex in range(len(simplex)):
				new_simplex.append(simplex[vertex][:])
			new_chi2 = chi2[:]


			# Reflection.
			#############
			reflection_vector = move(simplex[index_high], 1.0)
			reflection_chi2 = chi2_func(values, function(function_options, reflection_vector), errors)
			if print_flag == 2:
				print "%-29s%-40s" % ("Reflection vector:", `reflection_vector`)
				print "%-29s%-40s" % ("Reflection chi2:", `reflection_chi2`)

			# Update simplex with the reflection vector.
			if reflection_chi2 < chi2[index_high]:
				new_simplex[index_high] = reflection_vector[:]
				new_chi2[index_high] = reflection_chi2


			# Extension.
			############
			if reflection_chi2 <= index_low]:
				extension_vector = move(simplex[index_high], 2.0)
				extension_chi2 = chi2_func(values, function(function_options, extension_vector), errors)
				if print_flag == 2:
					print "%-29s%-40s" % ("Extension vector:", `extension_vector`)
					print "%-29s%-40s" % ("Extension chi2:", `extension_chi2`)

				# Update simplex with the extension vector.
				if extension_chi2 <= chi2[index_high]:
					new_simplex[index_high] = extension_vector[:]
					new_chi2[index_high] = extension_chi2


			# Contraction.
			##############
			elif reflection_chi2 >= chi2[index_2nd_high]:
				contract_vector = move(simplex[index_high], -0.5)
				contract_chi2 = chi2_func(values, function(function_options, contract_vector), errors)
				if print_flag == 2:
					print "%-29s%-40s" % ("Contraction vector:", `contract_vector`)
					print "%-29s%-40s" % ("Contraction chi2:", `contract_chi2`)

				# Update simplex with the contraction vector.
				if contract_chi2 <= chi2[index_high]:
					new_simplex[index_high] = contract_vector[:]
					new_chi2[index_high] = contract_chi2


				# Shrink.
				#########
				# This code has not been debugged!!!
				if contract_chi2 >= chi2[index_high]:
					# Loop over the vertices.
					for vertex in range(len(simplex)):
						if vertex == index_low:
							continue
						shrink_vector = []
						# Loop over the parameters.
						for param in range(len(simplex[0])):
							new_param = 0.5 * simplex[index_low][param] + simplex[vertex][param]
							shrink_vector.append(new_param)
						new_simplex[vertex] = shrink_vector[:]
					if print_flag == 2:
						print "Shrinking"
						print "\t%-29s%-40s" % ("Old simplex:", `simplex`)
						print "\t%-29s%-40s" % ("New simplex:", `new_simplex`)


			# Update the simplex and chi-squared vector.
			for vertex in range(len(simplex)):
				simplex[vertex] = new_simplex[vertex][:]
			chi2 = new_chi2[:]

			# Print debugging info
			if print_flag == 2:
				print "%-29s%-40s" % ("New simplex:", `simplex`)
				print "%-29s%-40s" % ("New chi-squared vector:", `chi2`)

			minimise_num = minimise_num + 1

		if print_flag >= 1:
			print "The final simplex is: " + `simplex`
			print "The final chi2 vector is: " + `chi2`

		factor = factor / 10.0
		num_runs = num_runs + runs

	print "\n\nTotal number of runs: " + `num_runs`

	return simplex[index_low], chi2[index_low], minimise_num


def create_simplex(params, grid_ops, factor):
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


def move(vertex, factor):
	"Function to do something?"

	# Calculate the new vector.
	new_vector = []
	for param in range(len(simplex[0])):
		new = ave_vector[param] * (1 + factor) - factor * vertex[param]
		new_vector.append(new)

	return new_vector

