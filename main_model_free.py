import sys
from re import match
from scipy.optimize import fmin, fmin_bfgs, fmin_ncg, fmin_powell
simplex = fmin
powell = fmin_powell
bfgs = fmin_bfgs
newton = fmin_ncg

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
		diff_type = 'iso'
		diff_params = (float(10.0 * 1e-9))
		mf_model = self.mf.data.model

		# Flags.
		########

		# Debugging flag
		self.mf.min_debug = 2

		# Limits flag, 0 = no limits, 1 = set limits.
		limits_flag = 0

		grid_ops = []
		limits = []
		self.mf.results.write("%-5s" % "Num")
		self.mf.results.write("%-6s" % "Name")
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
			grid_ops.append([20.0, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
			limits.append([0.0, 1.0])
			limits.append([0.0, 100.0 / (1e-8 * self.mf.data.frq[0])**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
		elif match('m4', self.mf.data.model):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
			grid_ops.append([20.0, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
			limits.append([0.0, 1.0])
			limits.append([0.0 * 1e-12, 10000.0 * 1e-12])
			limits.append([0.0, 100.0 / (1e-8 * self.mf.data.frq[0])**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
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
		self.mf.results.write("%-30s\n" % "Chi-squared statistic")


		# Loop over all data sets.
		for res in range(len(self.mf.data.relax_data[0])):
			if self.mf.min_debug >= 1:
				print "\n\n<<< Fitting to residue: " + self.mf.data.relax_data[0][res][0] + " " + self.mf.data.relax_data[0][res][1] + " >>>"
				print "\n\n<<< Grid search >>>"
			else:
				print "Residue: " + self.mf.data.relax_data[0][res][0] + " " + self.mf.data.relax_data[0][res][1]

			# Initialise the relaxation data and error data structures.
			relax_data = []
			errors = []
			for data in range(len(self.mf.data.relax_data)):
				relax_data.append(self.mf.data.relax_data[data][res][2])
				errors.append(self.mf.data.relax_data[data][res][3])
			function_ops = ( diff_type, diff_params, mf_model, relax_data, errors )

			# Grid search.
			params, chi2 = self.mf.minimise.grid.search(self.mf.mf_functions.chi2.calc, fargs=function_ops, args=grid_ops)
			if self.mf.min_debug >= 1:
				print "\nThe grid parameters are: " + `params`
				print "The grid chi-squared value is: " + `chi2`

			#params = [0.368]
			#params = [0.368, 0.0]
			#params = [0.950, 0.585, 33.0*1e-12]
			#params = [0.900, 0.0*1e-12, 0.0/(1e-8 * self.mf.data.frq[0])**2]
			#params = [0.900, 100*1e-12, 2.76038451e-17]
			#params = [6.31578947e-01, 8.42105263e-01, 5.26315789e-10]
			#chi2 = 0.0

			# Simplex minimisation.
			if match('Simplex', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Simplex minimisation >>>"
				output = simplex(self.mf.mf_functions.chi2.calc, params, args=function_ops, xtol=1e-15, ftol=1e-15, maxiter=10000, maxfun=10000, full_output=1, disp=self.mf.min_debug)
				params, chi2, iter, num_func_calls, warn_flag = output
				print "mf params:  " + `params`
				print "chi2:       " + `chi2`
				print "iter:       " + `iter`
				print "func calls: " + `num_func_calls`
				print "warn flag:  " + `warn_flag`

			# Modified Powell minimisation.
			elif match('Powell', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Powell minimisation >>>"
				output = powell(self.mf.mf_functions.chi2.calc, params, args=function_ops, xtol=1e-15, ftol=1e-15, maxiter=10000, maxfun=10000, full_output=1, disp=self.mf.min_debug)
				params, chi2, iter, num_func_calls, warn_flag = output
			
			# Levenberg-Marquardt minimisation.
			elif match('LM', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Levenberg-Marquardt minimisation >>>"

				#params, chi2 = self.mf.minimise.levenberg_marquardt.fit(self.mf.mf_functions.chi2.calc, params, self.mf.mf_functions.dchi.calc, args=function_ops, relax_data, errors)

			# Quasi-Newton BFGS minimisation.
			elif match('BFGS', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
				output = bfgs(self.mf.mf_functions.chi2.calc, params, fprime=self.mf.mf_functions.dchi2.calc, args=function_ops, avegtol=1e-15, maxiter=10000, full_output=1, disp=self.mf.min_debug)
				params, chi2, num_func_calls, num_grad_calls, warn_flag = output

			# Newton Conjugate Gradient minimisation.
			elif match('Newton', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Newton Conjugate Gradient minimisation >>>"
				output = newton(self.mf.mf_functions.chi2.calc, params, fprime=self.mf.mf_functions.dchi2.calc, fhess_p=None, fhess=self.mf.mf_functions.d2chi2.calc, args=function_ops, maxiter=10000, full_output=1, disp=self.mf.min_debug)
				params, chi2, num_func_calls, num_grad_calls, num_hessian_calls, warn_flag = output

			# None.
			else:
				raise NameError, "Minimiser type set incorrectly\n"
				sys.exit()

			if self.mf.min_debug >= 1:
				print "\n\n<<< Finished minimiser >>>"
				print "The final parameters are: " + `params`
				print "The final chi-squared value is: " + `chi2` + "\n"

			self.mf.results.write("%-5s" % self.mf.data.relax_data[data][res][0])
			self.mf.results.write("%-6s" % self.mf.data.relax_data[data][res][1])
			if match('m1', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
			elif match('m2', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * 1e12`)
			elif match('m3', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * (1e-8 * self.mf.data.frq[0])**2`)
			elif match('m4', self.mf.data.model):
				self.mf.results.write("%-30s" % `params[0]`)
				self.mf.results.write("%-30s" % `params[1] * 1e12`)
				self.mf.results.write("%-30s" % `params[2] * (1e-8 * self.mf.data.frq[0])**2`)
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
