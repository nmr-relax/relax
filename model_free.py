from Numeric import Float64, array
from re import match
import sys

from common_ops import common_ops
from functions.mf_functions import mf_functions
from functions.mf_trans_functions import mf_trans_functions


class model_free(common_ops):
	def __init__(self, relax):
		"Class used to create and process input and output for the program Modelfree 4."

		self.relax = relax

		self.update_data()
		self.ask_stage()
		if match('1', self.relax.data.stage):
			self.minimisation()
		elif match('^2', self.relax.data.stage):
			self.model_selection()


	def minimisation(self):
		self.extract_relax_data()
		self.relax.data.calc_frq()
		self.relax.data.calc_constants()

		self.relax.file_ops.mkdir(self.relax.data.model)
		self.relax.results = open(self.relax.data.model + '/results', 'w')

		print "\n\n[ Model-free fitting ]\n"
		diff_type = 'iso'
		diff_params = (float(10.0 * 1e-9))
		mf_model = self.relax.data.model

		# Flags.
		########

		# Debugging flag
		self.relax.min_debug = 1

		# Flag for the diagonal scaling of the model-free parameters.
		self.scaling_flag = 1

		# Minimisation options.
		chi2_tol = 1e-15
		max_iterations = 5000

		# Set the function, gradient, and hessian functions.
		if self.scaling_flag:
			self.functions = mf_trans_functions(self.mf)
			func = self.functions.chi2
			dfunc = self.functions.dchi2
			d2func = self.functions.d2chi2
		else:
			self.functions = mf_functions(self.mf)
			func = self.functions.chi2
			dfunc = self.functions.dchi2
			d2func = self.functions.d2chi2

		# The value of the constant.
		self.c = 1e10

		# Initialise the grid options.
		if match('[Gg]rid', self.relax.usr_param.init_params[0]):
			init_params = [self.relax.usr_param.init_params[0], self.init_grid_ops()]

		# Initialise the fixed model-free parameter options.
		elif match('[Ff]ixed', self.relax.usr_param.init_params[0]):
			init_params = [self.relax.usr_param.init_params[0], self.init_fixed_params()]

		# Initialise the Levenberg-Marquardt minimisation options.
		if match('[Ll][Mm]$', self.relax.usr_param.minimiser[0]) or match('[Ll]evenburg-[Mm]arquardt$', self.relax.usr_param.minimiser[0]):
			if self.scaling_flag:
				self.relax.usr_param.minimiser.append(mf_trans_functions.lm_dri)
			else:
				self.relax.usr_param.minimiser.append(mf_functions.lm_dri)
			self.relax.usr_param.minimiser.append([])

		# Print a header into the results file.
		self.print_header()

		# Loop over all data sets.
		for self.res in range(len(self.relax.data.relax_data[0])):
			if self.relax.min_debug >= 1:
				print "\n\n<<< Fitting to residue: " + self.relax.data.relax_data[0][self.res][0] + " " + self.relax.data.relax_data[0][self.res][1] + " >>>"
			else:
				print "Residue: " + self.relax.data.relax_data[0][self.res][0] + " " + self.relax.data.relax_data[0][self.res][1]

			# Initialise the iteration counter and function, gradient, and hessian call counters.
			self.iter_count = 0
			self.f_count = 0
			self.g_count = 0
			self.h_count = 0

			# Initialise the relaxation data and error data structures.
			relax_data = []
			errors = []
			for data in range(len(self.relax.data.relax_data)):
				relax_data.append(self.relax.data.relax_data[data][self.res][2])
				errors.append(self.relax.data.relax_data[data][self.res][3])
			function_ops = (diff_type, diff_params, mf_model, relax_data, errors)
			if match('^[Ll][Mm]$', self.relax.usr_param.minimiser[0]) or match('^[Ll]evenburg-[Mm]arquardt$', self.relax.usr_param.minimiser[0]):
				self.relax.usr_param.minimiser[2] = errors

			# Initialisation of model-free parameter values.
			results = self.relax.minimise(func, dfunc=dfunc, d2func=d2func, args=function_ops, x0=None, minimiser=init_params, full_output=1, print_flag=self.relax.min_debug)
			self.params, self.chi2, iter, fc, gc, hc, self.warning = results

			# Minimisation.
			results = self.relax.minimise(func, dfunc=dfunc, d2func=d2func, args=function_ops, x0=self.params, minimiser=self.relax.usr_param.minimiser, func_tol=chi2_tol, maxiter=max_iterations, full_output=1, print_flag=self.relax.min_debug)
			self.params, self.chi2, iter, fc, gc, hc, self.warning = results
			self.iter_count = self.iter_count + iter
			self.f_count = self.f_count + fc
			self.g_count = self.g_count + gc
			self.h_count = self.h_count + hc

			if self.relax.min_debug:
				print "\n\n<<< Finished minimiser >>>"

			# Write the results to file.
			self.print_results()

		print "\n[ Done ]\n\n"
		self.relax.results.close()


	def model_selection(self):
		"Model selection stage."

	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for model-free analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):  Minimisation."
		print "   Stage 2 (2):  Model selection."

		while 1:
			input = raw_input('> ')
			valid_stages = ['1', '2']
			if input in valid_stages:
				self.relax.data.stage = input
				break
			else:
				print "Invalid stage number.  Choose either 1 or 2."
		if match('1', self.relax.data.stage):
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
					self.relax.data.model = 'm' + input
					break
				else:
					print "Invalid model-free model."
		elif match('2', self.relax.data.stage):
			while 1:
				print "Stage 2 has the following two options for the final run:"
				print "   (a):   No optimization of the diffusion tensor."
				print "   (b):   Optimization of the diffusion tensor."
				input = raw_input('> ')
				valid_stages = ['a', 'b']
				if input in valid_stages:
					self.relax.data.stage = self.relax.data.stage + input
					break
				else:
					print "Invalid option, choose either a or b."

		print "The stage chosen is " + self.relax.data.stage + "\n"
		if match('1', self.relax.data.stage):
			print "The model-free model chosen is " + self.relax.data.model
		print "\n"


	def init_fixed_params(self):
		"""Fix the inital model-free parameter values.

		The function needs to be modified so the user can specify the fixed values.
		"""

		if match('m1', self.relax.data.model):
			params = array([0.5], Float64)
		elif match('m2', self.relax.data.model):
			if self.scaling_flag:
				params = array([0.5, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 100.0 * 1e-12], Float64)
		elif match('m3', self.relax.data.model):
			params = array([0.5, 0.0], Float64)
		elif match('m4', self.relax.data.model):
			if self.scaling_flag:
				params = array([0.5, 0.0, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 0.0, 100.0 * 1e-12], Float64)
		elif match('m5', self.relax.data.model):
			if self.scaling_flag:
				params = array([0.5, 0.5, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 0.5, 100.0 * 1e-12], Float64)

		return params


	def init_grid_ops(self):
		"""Generate the data structure of grid options for the grid search.

		The function needs to be modified so the user can specify the number of iterations for each parameter.
		"""

		inc = self.relax.usr_param.init_params[1]
		grid_ops = []
		if match('m1', self.relax.data.model):
			grid_ops.append([inc, 0.0, 1.0])
		elif match('m2', self.relax.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])
		elif match('m3', self.relax.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			grid_ops.append([inc, 0.0, 30.0 / (1e-8 * self.relax.data.frq[0])**2])
		elif match('m4', self.relax.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])
			grid_ops.append([inc, 0.0, 30.0 / (1e-8 * self.relax.data.frq[0])**2])
		elif match('m5', self.relax.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])

		return grid_ops


	def print_header(self):
		self.relax.results.write("%-5s" % "Num")
		self.relax.results.write("%-6s" % "Name")
		if match('m1', self.relax.data.model):
			self.relax.results.write("%-30s" % "S2")
		elif match('m2', self.relax.data.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % "te (ps)")
		elif match('m3', self.relax.data.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
		elif match('m4', self.relax.data.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % "te (ps)")
			self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
		elif match('m5', self.relax.data.model):
			self.relax.results.write("%-30s" % "S2f")
			self.relax.results.write("%-30s" % "S2s")
			self.relax.results.write("%-30s" % "ts (ps)")
		self.relax.results.write("%-30s" % "Chi-squared statistic")
		self.relax.results.write("%-15s" % "Iterations")
		self.relax.results.write("%-15s" % "Func calls")
		self.relax.results.write("%-15s" % "Grad calls")
		self.relax.results.write("%-15s" % "Hessian calls")
		self.relax.results.write("%-30s\n" % "Warning")


	def print_results(self):
		self.relax.results.write("%-5s" % self.relax.data.relax_data[0][self.res][0])
		self.relax.results.write("%-6s" % self.relax.data.relax_data[0][self.res][1])
		if match('m1', self.relax.data.model):
			s2 = self.params[0]
			print "S2: " + `s2` + " Chi2: " + `self.chi2`
			self.relax.results.write("%-30s" % `s2`)
		elif match('m2', self.relax.data.model):
			s2 = self.params[0]
			if self.scaling_flag:
				te = self.params[1] * 1e12 / self.c
			else:
				te = self.params[1] * 1e12
			print "S2: " + `s2` + " te: " + `te` + " Chi2: " + `self.chi2`
			self.relax.results.write("%-30s" % `s2`)
			self.relax.results.write("%-30s" % `te`)
		elif match('m3', self.relax.data.model):
			s2 = self.params[0]
			rex = self.params[1] * (1e-8 * self.relax.data.frq[0])**2
			print "S2: " + `s2` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
			self.relax.results.write("%-30s" % `s2`)
			self.relax.results.write("%-30s" % `rex`)
		elif match('m4', self.relax.data.model):
			s2 = self.params[0]
			if self.scaling_flag:
				te = self.params[1] * 1e12 / self.c
			else:
				te = self.params[1] * 1e12
			rex = self.params[2] * (1e-8 * self.relax.data.frq[0])**2
			print "S2: " + `s2` + " te: " + `te` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
			self.relax.results.write("%-30s" % `s2`)
			self.relax.results.write("%-30s" % `te`)
			self.relax.results.write("%-30s" % `rex`)
		elif match('m5', self.relax.data.model):
			s2f = self.params[0]
			s2s = self.params[1]
			if self.scaling_flag:
				ts = self.params[2] * 1e12 / self.c
			else:
				ts = self.params[2] * 1e12
			print "S2f: " + `s2f` + " S2s: " + `s2s` + " ts: " + `ts` + " Chi2: " + `self.chi2`
			self.relax.results.write("%-30s" % `s2f`)
			self.relax.results.write("%-30s" % `s2s`)
			self.relax.results.write("%-30s" % `ts`)
		self.relax.results.write("%-30s" % `self.chi2`)
		self.relax.results.write("%-15s" % `self.iter_count`)
		self.relax.results.write("%-15s" % `self.f_count`)
		self.relax.results.write("%-15s" % `self.g_count`)
		self.relax.results.write("%-15s" % `self.h_count`)
		if self.warning:
			self.relax.results.write("%-30s\n" % `self.warning`)
		else:
			self.relax.results.write("\n")
