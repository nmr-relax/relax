import sys
from re import match

class main_model_free:
	def __init__(self, mf):
		"Class used to create and process input and output for the program Modelfree 4."

		self.mf = mf

		self.mf.data.stage, self.mf.data.model = self.ask_stage()
		self.mf.file_ops.mkdir(self.mf.data.model)
		self.mf.common_ops.extract_relax_data()
		self.mf.results = open(self.mf.data.model + '/results', 'w')
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		
		print "\n\n[ Model-free fitting ]\n"
		function_ops = ['iso', [float(10.0 * 1e-9)], self.mf.data.model]

		# Flags.
		########

		# Debugging flag
		self.mf.min_debug = 1

		# Derivative flag, 0 = no derivatives, 1 = calculate derivatives.
		derivatives_flag = 0

		# Limits flag, 0 = no limits, 1 = set limits.
		limits_flag = 0
		
		grid_ops = []
		limits = []
		if match('m1', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			limits.append([0.0, 1.0])
			self.mf.results.write("%-30s" % "S2")
		elif match('m2', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
			limits.append([0.0, 1.0])
			limits.append([0.0 * 1e-12, 10000.0 * 1e-12])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
		elif match('m3', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 30.0 / self.mf.data.frq[0]**2])
			limits.append([0.0, 1.0])
			limits.append([0.0, 100.0 / self.mf.data.frq[0]**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "Rex")
		elif match('m4', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
			grid_ops.append([20.0, 0.0, 30.0 / self.mf.data.frq[0]**2])
			limits.append([0.0, 1.0])
			limits.append([0.0 * 1e-12, 10000.0 * 1e-12])
			limits.append([0.0, 100.0 / self.mf.data.frq[0]**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
			self.mf.results.write("%-30s" % "Rex")
		elif match('m5', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
			limits.append([0.0, 1.0])
			limits.append([0.0, 1.0])
			limits.append([0.0 * 1e-12, 10000.0 * 1e-12])
			self.mf.results.write("%-30s" % "S2f")
			self.mf.results.write("%-30s" % "S2s")
			self.mf.results.write("%-30s" % "ts (ps)")
		self.mf.results.write("%-30s\n" % "chi-squared statistic")


		# Loop over all data sets.
		for res in range(len(self.mf.data.relax_data[0])):
			if self.mf.min_debug >= 1:
				print "\n\n<<< Fitting to residue: " + self.mf.data.relax_data[0][res][0] + " " + self.mf.data.relax_data[0][res][1] + " >>>"
				print "\n\n<<< Grid search >>>"
			else:
				print "Residue: " + self.mf.data.relax_data[0][res][0] + " " + self.mf.data.relax_data[0][res][1]

			# Initialise some data structures.
			values = []
			errors = []
			for data in range(len(self.mf.data.relax_data)):
				values.append(self.mf.data.relax_data[data][res][2])
				errors.append(self.mf.data.relax_data[data][res][3])


			# Grid search.
			derivative_flag = 0   # Derivative flag, turned off because not needed in grid search.
			params, chi2 = self.mf.minimise.grid.search(self.mf.functions.relax.Ri, function_ops, derivative_flag, self.mf.functions.chi2.relax_data, values, errors, grid_ops)
			if self.mf.min_debug >= 1:
				print "\nThe grid parameters are: " + `params`
				print "The grid chi-squared value is: " + `chi2`

			#params = [0.368]
			#params = [0.368, 0.0]
			#params = [0.368, 0.0, 0.0]

			# Simplex minimisation.
			if match('Simplex', self.mf.usr_param.minimiser):
				if match('m1', self.mf.data.model):
					print "One dimensional simplex minimisation, quitting program!"
				if self.mf.min_debug >= 1:
					print "\n\n<<< Simplex minimisation >>>"
				factor = 1.0
				num_runs = 0.0
				for i in range(10):
					self.simplex = self.create_simplex(params, grid_ops, factor)
					if self.mf.min_debug >= 1:
						print "\nThe initial simplex is: " + `self.simplex`
					params, chi2, runs = self.mf.minimise.simplex.fit(self.mf.functions.relax.Ri, function_ops, derivative_flag, self.mf.functions.chi2.relax_data, values, errors, self.simplex)
					factor = factor / 10.0
					num_runs = num_runs + runs
				print "\n\nTotal number of runs: " + `num_runs`

			# Levenberg-Marquardt minimisation.
			elif match('LM', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Levenberg-Marquardt minimisation >>>"

				derivative_flag = 1   # Derivative flag, turned no because needed by Levenberg-Marquardt minimisation.
				params, chi2 = self.mf.minimise.levenberg_marquardt.fit(self.mf.functions.relax.Ri, function_ops, derivative_flag, self.mf.functions.chi2.relax_data, values, errors, params, limits_flag, limits)
		
			if self.mf.min_debug >= 1:
				print "\n\n<<< Finished minimiser >>>"
				print "The final parameters are: " + `params`
				print "The final chi-squared value is: " + `chi2` + "\n"

			if match('m1', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
			elif match('m2', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * 1e12`)
			elif match('m3', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * self.mf.data.frq[0]**2`)
			elif match('m4', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * 1e12`)
				self.mf.results.write("%-30s" % `params[2] * self.mf.data.frq[0]**2`)
			elif match('m5', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1]`)
				self.mf.results.write("%-30s" % `params[2] * 1e12`)
			self.mf.results.write("%-30s\n" % `chi2`)

		print "\n[ Done ]\n\n"
		self.mf.results.close()


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for model-free analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):  Model-free fitting of the relaxation data."
		print "   Stage 2 (2):  Model selection."

		while 1:
			input = raw_input('> ')
			valid_stages = ['1', '2']
			if input in valid_stages:
				stage = input
				break
			else:
				print "Invalid stage number.  Choose either 1 or 2."
		if match('1', stage):
			while 1:
				print "Please select which model-free model to fit to."
				print "   (1): Model-free model 1, {S2}."
				print "   (2): Model-free model 2, {S2, te}."
				print "   (3): Model-free model 3, {S2, Rex}."
				print "   (4): Model-free model 4, {S2, te, Rex}."
				print "   (5): Model-free model 5, {S2f, S2s, ts}."
				input = raw_input('> ')
				valid_stages = ['1', '2', '3', '4', '5']
				if input in valid_stages:
					model = input
					break
				else:
					print "Invalid model-free model."

		print "The stage chosen is " + stage
		if match('1', stage):
			print "The model-free model chosen is " + model
		print "\n"

		return stage, 'm' + model


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


