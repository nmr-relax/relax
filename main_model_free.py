import sys
from Numeric import array
from re import match
try:
	from scipy.optimize import fmin, fmin_bfgs, fmin_ncg
	simplex_scipy = fmin
	bfgs_scipy = fmin_bfgs
	ncg_scipy = fmin_ncg
	noscipy_flag = 0
except ImportError:
	print "Python module scipy not installed, cannot use simplex, BFGS, or Newton conjugate gradient minimisation."
	noscipy_flag = 1


class main_model_free:
	def __init__(self, mf):
		"Class used to create and process input and output for the program Modelfree 4."

		self.mf = mf
		self.lm = self.mf.minimise.levenberg_marquardt
		self.steepest_descent = self.mf.minimise.steepest_descent
		self.coordinate_descent = self.mf.minimise.coordinate_descent
		self.newton = self.mf.minimise.newton
		self.bfgs = self.mf.minimise.bfgs

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
		self.mf.min_debug = 1

		# Transformation flag.
		trans_flag = 1

		# Options.
		tol = 1e-15
		max = 10000

		# Set the function, gradient, and hessian functions.
		if trans_flag:
			func = self.mf.mf_trans_functions.chi2
			dfunc = self.mf.mf_trans_functions.dchi2
			d2func = self.mf.mf_trans_functions.d2chi2
			lm_dfunc = self.mf.mf_trans_functions.lm_dri
		else:
			func = self.mf.mf_functions.chi2
			dfunc = self.mf.mf_functions.dchi2
			d2func = self.mf.mf_functions.d2chi2
			lm_dfunc = self.mf.mf_functions.lm_dri

		# The value of the constant.
		self.c = 1e10
 
		grid_ops = []
		self.mf.results.write("%-5s" % "Num")
		self.mf.results.write("%-6s" % "Name")
		if match('m1', self.mf.data.model):
			grid_ops.append([21.0, 0.0, 1.0])
			self.mf.results.write("%-30s" % "S2")
		elif match('m2', self.mf.data.model):
			grid_ops.append([21.0, 0.0, 1.0])
			if trans_flag:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
		elif match('m3', self.mf.data.model):
			grid_ops.append([21.0, 0.0, 1.0])
			grid_ops.append([21.0, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
		elif match('m4', self.mf.data.model):
			grid_ops.append([21.0, 0.0, 1.0])
			if trans_flag:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12])
			grid_ops.append([21.0, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
		elif match('m5', self.mf.data.model):
			grid_ops.append([21.0, 0.0, 1.0])
			grid_ops.append([21.0, 0.0, 1.0])
			if trans_flag:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([21.0, 0.0, 10000.0 * 1e-12])
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

			line_search = self.mf.minimise.line_search_more_thuente
			#line_search = self.mf.minimise.backtrack_line
			type = "More and Thuente"

			# Grid search.
			params, chi2 = self.mf.minimise.grid(func, grid_ops, args=function_ops, print_flag=self.mf.min_debug)
			if self.mf.min_debug >= 1:
				print "\nThe grid parameters are: " + `params`
				print "The grid chi-squared value is: " + `chi2`

			#params = [0.368]
			#params = [0.368, 0.0]
			#params = [0.900, 0.0*1e-12, 0.0/(1e-8 * self.mf.data.frq[0])**2]
			#params = [0.900, 100*1e-12, 2.76038451e-17]
			#params = [6.31578947e-01, 8.42105263e-01, 5.26315789e-10]
			#if trans_flag:
			#	params = array([0.5, 0.5, 1e-12 * self.c])
			#else:
			#	params = array([0.5, 0.5, 1e-12])
			#chi2 = 0.0
			#print "Params: " + `params`
			#print "Chi2: " + `chi2`

			# Simplex minimisation (scipy).
			if match('^[Ss]implex[ _][Ss]cipy$', self.mf.usr_param.minimiser):
				if noscipy_flag:
					print "Simplex minimisation has been choosen yet the scipy python module has not been installed."
					sys.exit()
				if self.mf.min_debug >= 1:
					print "\n\n<<< Simplex minimisation (scipy) >>>"
				output = simplex_scipy(func, params, args=function_ops, xtol=1e-15, ftol=tol, maxiter=max, maxfun=10000, full_output=1, disp=self.mf.min_debug)
				params, chi2, iter, num_func_calls, warn_flag = output
				print "iter:       " + `iter`
				print "func calls: " + `num_func_calls`
				print "warn flag:  " + `warn_flag`

			# Levenberg-Marquardt minimisation.
			elif match('^[Ll][Mm]$', self.mf.usr_param.minimiser) or match('^[Ll]evenburg-[Mm]arquardt$', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Levenberg-Marquardt minimisation >>>"
				output = self.lm(func, dfunc, lm_dfunc, params, errors, args=function_ops, tol=tol, maxiter=max, full_output=1, print_flag=self.mf.min_debug)
				params, chi2, iter, warn_flag = output
				print "iter:       " + `iter`
				print "warn flag:  " + `warn_flag`

			# Back-and-forth coordinate descent minimisation.
			elif match('^[Cc][Dd]$', self.mf.usr_param.minimiser) or match('^[Cc]oordinate-[Dd]escent$', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Back-and-forth coordinate descent minimisation >>>"
				output = self.coordinate_descent(func, dfunc, params, line_search, args=function_ops, tol=tol, maxiter=max, full_output=1)
				params, chi2, iter, warn_flag = output
				print "iter:       " + `iter`
				print "warn flag:  " + `warn_flag`

			# Steepest descent minimisation.
			elif match('^[Ss][Dd]$', self.mf.usr_param.minimiser) or match('^[Ss]teepest[ _][Dd]escent$', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Steepest descent minimisation >>>"
				output = self.steepest_descent(func, dfunc, params, line_search, args=function_ops, tol=tol, maxiter=max, full_output=1)
				params, chi2, iter, warn_flag = output
				print "iter:       " + `iter`
				print "warn flag:  " + `warn_flag`
			
			# Quasi-Newton BFGS minimisation.
			elif match('^[Bb][Ff][Gg][Ss]$', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Quasi-Newton BFGS minimisation >>>"
				output = self.bfgs(func, dfunc, params, line_search, args=function_ops, tol=tol, maxiter=max, full_output=1)
				params, chi2, iter, warn_flag = output
				print "iter:       " + `iter`
				print "warn flag:  " + `warn_flag`

			# Quasi-Newton BFGS minimisation (scipy).
			elif match('^[Bb][Ff][Gg][Ss][ _][Ss]cipy$', self.mf.usr_param.minimiser):
				if noscipy_flag:
					print "Quasi-Newton BFGS minimisation from the scipy python module has been choosen yet the module has not been installed."
					sys.exit()
				if self.mf.min_debug >= 1:
					print "\n\n<<< Quasi-Newton BFGS minimisation (scipy) >>>"
				output = bfgs_scipy(func, params, fprime=dfunc, args=function_ops, avegtol=tol, maxiter=max, full_output=1, disp=self.mf.min_debug)
				params, chi2, num_func_calls, num_grad_calls, warn_flag = output

			# Newton minimisation.
			elif match('^[Nn]ewton$', self.mf.usr_param.minimiser):
				if self.mf.min_debug >= 1:
					print "\n\n<<< Newton minimisation >>>"
				output = self.newton(func, dfunc, d2func, params, type, line_search, args=function_ops, tol=tol, maxiter=max, full_output=1)
				params, chi2, iter, warn_flag = output
				print "iter:       " + `iter`
				print "warn flag:  " + `warn_flag`

			# Newton Conjugate Gradient minimisation (scipy).
			elif match('^[Nn][Cc][Gg][ _][Ss]cipy$', self.mf.usr_param.minimiser):
				if noscipy_flag:
					print "Newton Conjugate Gradient minimisation has been choosen yet the scipy python module has not been installed."
					sys.exit()
				if self.mf.min_debug >= 1:
					print "\n\n<<< Newton Conjugate Gradient minimisation (scipy) >>>"
				output = ncg_scipy(func, params, fprime=dfunc, fhess=d2func, args=function_ops, avextol=tol, maxiter=max, full_output=1, disp=self.mf.min_debug)
				params, chi2, num_func_calls, num_grad_calls, num_hessian_calls, warn_flag = output

			# No match to minimiser string.
			else:
				raise NameError, "Minimiser type set incorrectly, " + `self.mf.usr_param.minimiser` + " not programmed.\n"
				sys.exit()

			if self.mf.min_debug >= 1:
				print "\n\n<<< Finished minimiser >>>"
				print "The final parameters are: " + `params`
				print "The final chi-squared value is: " + `chi2` + "\n"

			self.mf.results.write("%-5s" % self.mf.data.relax_data[data][res][0])
			self.mf.results.write("%-6s" % self.mf.data.relax_data[data][res][1])
			if match('m1', self.mf.data.model):
				s2 = params[0]
				print "S2: " + `s2` + " Chi2: " + `chi2`
				self.mf.results.write("%-30s" % `s2`)
			elif match('m2', self.mf.data.model):
				s2 = params[0]
				if trans_flag:
					te = params[1] * 1e12 / self.c
				else:
					te = params[1] * 1e12
				print "S2: " + `s2` + " te: " + `te` + " Chi2: " + `chi2`
				self.mf.results.write("%-30s" % `s2`)
				self.mf.results.write("%-30s" % `te`)
			elif match('m3', self.mf.data.model):
				s2 = params[0]
				rex = params[1] * (1e-8 * self.mf.data.frq[0])**2
				print "S2: " + `s2` + " Rex: " + `rex` + " Chi2: " + `chi2`
				self.mf.results.write("%-30s" % `s2`)
				self.mf.results.write("%-30s" % `rex`)
			elif match('m4', self.mf.data.model):
				s2 = params[0]
				if trans_flag:
					te = params[1] * 1e12 / self.c
				else:
					te = params[1] * 1e12
				rex = params[2] * (1e-8 * self.mf.data.frq[0])**2
				print "S2: " + `s2` + " te: " + `te` + " Rex: " + `rex` + " Chi2: " + `chi2`
				self.mf.results.write("%-30s" % `s2`)
				self.mf.results.write("%-30s" % `te`)
				self.mf.results.write("%-30s" % `rex`)
			elif match('m5', self.mf.data.model):
				s2f = params[0]
				s2s = params[1]
				if trans_flag:
					ts = params[2] * 1e12 / self.c
				else:
					ts = params[2] * 1e12
				print "S2f: " + `s2f` + " S2s: " + `s2s` + " ts: " + `ts` + " Chi2: " + `chi2`
				self.mf.results.write("%-30s" % `s2f`)
				self.mf.results.write("%-30s" % `s2s`)
				self.mf.results.write("%-30s" % `ts`)
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
