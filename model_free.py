from Numeric import Float64, array
from re import match
import sys

from common_ops import common_ops
from functions.mf_functions import mf_functions
from functions.mf_trans_functions import mf_trans_functions


class model_free(common_ops):
	def __init__(self, mf):
		"Class used to create and process input and output for the program Modelfree 4."

		self.mf = mf

		if self.mf.debug == 1:
			self.mf.file_ops.init_log_file()

		self.update_data()
		self.ask_stage()
		if match('1', self.mf.data.stage):
			self.minimisation_stage()
		elif match('^2', self.mf.data.stage):
			self.model_selection_stage()
		else:
			raise NameError, "No stage chosen."


	def minimisation_stage(self):
		self.extract_relax_data()
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()

		self.mf.file_ops.mkdir(self.mf.data.model)
		self.mf.results = open(self.mf.data.model + '/results', 'w')

		print "\n\n[ Model-free fitting ]\n"
		diff_type = 'iso'
		diff_params = (float(10.0 * 1e-9))
		mf_model = self.mf.data.model

		# Flags.
		########

		# Debugging flag
		self.mf.min_debug = 1

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
		if match('[Gg]rid', self.mf.usr_param.init_params[0]):
			init_params = [self.mf.usr_param.init_params[0], self.init_grid_ops()]

		# Initialise the fixed model-free parameter options.
		elif match('[Ff]ixed', self.mf.usr_param.init_params[0]):
			init_params = [self.mf.usr_param.init_params[0], self.init_fixed_params()]

		# Initialise the Levenberg-Marquardt minimisation options.
		if match('[Ll][Mm]$', self.mf.usr_param.minimiser[0]) or match('[Ll]evenburg-[Mm]arquardt$', self.mf.usr_param.minimiser[0]):
			if self.scaling_flag:
				self.mf.usr_param.minimiser.append(mf_trans_functions.lm_dri)
			else:
				self.mf.usr_param.minimiser.append(mf_functions.lm_dri)
			self.mf.usr_param.minimiser.append([])

		# Print a header into the results file.
		self.print_header()

		# Loop over all data sets.
		for self.res in range(len(self.mf.data.relax_data[0])):
			if self.mf.min_debug >= 1:
				print "\n\n<<< Fitting to residue: " + self.mf.data.relax_data[0][self.res][0] + " " + self.mf.data.relax_data[0][self.res][1] + " >>>"
			else:
				print "Residue: " + self.mf.data.relax_data[0][self.res][0] + " " + self.mf.data.relax_data[0][self.res][1]

			# Initialise the iteration counter and function, gradient, and hessian call counters.
			self.iter_count = 0
			self.f_count = 0
			self.g_count = 0
			self.h_count = 0

			# Initialise the relaxation data and error data structures.
			relax_data = []
			errors = []
			for data in range(len(self.mf.data.relax_data)):
				relax_data.append(self.mf.data.relax_data[data][self.res][2])
				errors.append(self.mf.data.relax_data[data][self.res][3])
			function_ops = (diff_type, diff_params, mf_model, relax_data, errors)
			if match('^[Ll][Mm]$', self.mf.usr_param.minimiser[0]) or match('^[Ll]evenburg-[Mm]arquardt$', self.mf.usr_param.minimiser[0]):
				self.mf.usr_param.minimiser[2] = errors

			# Initialisation of model-free parameter values.
			results = self.mf.minimise(func, dfunc=dfunc, d2func=d2func, args=function_ops, x0=None, minimiser=init_params, full_output=1, print_flag=self.mf.min_debug)
			self.params, self.chi2, iter, fc, gc, hc, self.warning = results

			# Minimisation.
			results = self.mf.minimise(func, dfunc=dfunc, d2func=d2func, args=function_ops, x0=self.params, minimiser=self.mf.usr_param.minimiser, func_tol=chi2_tol, maxiter=max_iterations, full_output=1, print_flag=self.mf.min_debug)
			self.params, self.chi2, iter, fc, gc, hc, self.warning = results
			self.iter_count = self.iter_count + iter
			self.f_count = self.f_count + fc
			self.g_count = self.g_count + gc
			self.h_count = self.h_count + hc

			if self.mf.min_debug:
				print "\n\n<<< Finished minimiser >>>"

			# Write the results to file.
			self.print_results()

		print "\n[ Done ]\n\n"
		self.mf.results.close()


	def model_selection_stage(self):
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
				self.mf.data.stage = input
				break
			else:
				print "Invalid stage number.  Choose either 1 or 2."
		if match('1', self.mf.data.stage):
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
					self.mf.data.model = 'm' + input
					break
				else:
					print "Invalid model-free model."
		elif match('2', self.mf.data.stage):
			while 1:
				print "Stage 2 has the following two options for the final run:"
				print "   (a):   No optimization of the diffusion tensor."
				print "   (b):   Optimization of the diffusion tensor."
				input = raw_input('> ')
				valid_stages = ['a', 'b']
				if input in valid_stages:
					self.mf.data.stage = self.mf.data.stage + input
					break
				else:
					print "Invalid option, choose either a or b."

		print "The stage chosen is " + self.mf.data.stage + "\n"
		if match('1', self.mf.data.stage):
			print "The model-free model chosen is " + self.mf.data.model
		print "\n"


	def init_fixed_params(self):
		"""Fix the inital model-free parameter values.

		The function needs to be modified so the user can specify the fixed values.
		"""

		if match('m1', self.mf.data.model):
			params = array([0.5], Float64)
		elif match('m2', self.mf.data.model):
			if self.scaling_flag:
				params = array([0.5, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 100.0 * 1e-12], Float64)
		elif match('m3', self.mf.data.model):
			params = array([0.5, 0.0], Float64)
		elif match('m4', self.mf.data.model):
			if self.scaling_flag:
				params = array([0.5, 0.0, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 0.0, 100.0 * 1e-12], Float64)
		elif match('m5', self.mf.data.model):
			if self.scaling_flag:
				params = array([0.5, 0.5, 100.0 * 1e-12 * self.c], Float64)
			else:
				params = array([0.5, 0.5, 100.0 * 1e-12], Float64)

		return params


	def init_grid_ops(self):
		"""Generate the data structure of grid options for the grid search.

		The function needs to be modified so the user can specify the number of iterations for each parameter.
		"""

		inc = self.mf.usr_param.init_params[1]
		grid_ops = []
		if match('m1', self.mf.data.model):
			grid_ops.append([inc, 0.0, 1.0])
		elif match('m2', self.mf.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])
		elif match('m3', self.mf.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			grid_ops.append([inc, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
		elif match('m4', self.mf.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])
			grid_ops.append([inc, 0.0, 30.0 / (1e-8 * self.mf.data.frq[0])**2])
		elif match('m5', self.mf.data.model):
			grid_ops.append([inc, 0.0, 1.0])
			grid_ops.append([inc, 0.0, 1.0])
			if self.scaling_flag:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12 * self.c])
			else:
				grid_ops.append([inc, 0.0, 10000.0 * 1e-12])

		return grid_ops


	def print_header(self):
		self.mf.results.write("%-5s" % "Num")
		self.mf.results.write("%-6s" % "Name")
		if match('m1', self.mf.data.model):
			self.mf.results.write("%-30s" % "S2")
		elif match('m2', self.mf.data.model):
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
		elif match('m3', self.mf.data.model):
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
		elif match('m4', self.mf.data.model):
			self.mf.results.write("%-30s" % "S2")
			self.mf.results.write("%-30s" % "te (ps)")
			self.mf.results.write("%-30s" % ("Rex (" + self.mf.data.frq_label[0] + " MHz)"))
		elif match('m5', self.mf.data.model):
			self.mf.results.write("%-30s" % "S2f")
			self.mf.results.write("%-30s" % "S2s")
			self.mf.results.write("%-30s" % "ts (ps)")
		self.mf.results.write("%-30s" % "Chi-squared statistic")
		self.mf.results.write("%-15s" % "Iterations")
		self.mf.results.write("%-15s" % "Func calls")
		self.mf.results.write("%-15s" % "Grad calls")
		self.mf.results.write("%-15s" % "Hessian calls")
		self.mf.results.write("%-30s\n" % "Warning")


	def print_results(self):
		self.mf.results.write("%-5s" % self.mf.data.relax_data[0][self.res][0])
		self.mf.results.write("%-6s" % self.mf.data.relax_data[0][self.res][1])
		if match('m1', self.mf.data.model):
			s2 = self.params[0]
			print "S2: " + `s2` + " Chi2: " + `self.chi2`
			self.mf.results.write("%-30s" % `s2`)
		elif match('m2', self.mf.data.model):
			s2 = self.params[0]
			if self.scaling_flag:
				te = self.params[1] * 1e12 / self.c
			else:
				te = self.params[1] * 1e12
			print "S2: " + `s2` + " te: " + `te` + " Chi2: " + `self.chi2`
			self.mf.results.write("%-30s" % `s2`)
			self.mf.results.write("%-30s" % `te`)
		elif match('m3', self.mf.data.model):
			s2 = self.params[0]
			rex = self.params[1] * (1e-8 * self.mf.data.frq[0])**2
			print "S2: " + `s2` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
			self.mf.results.write("%-30s" % `s2`)
			self.mf.results.write("%-30s" % `rex`)
		elif match('m4', self.mf.data.model):
			s2 = self.params[0]
			if self.scaling_flag:
				te = self.params[1] * 1e12 / self.c
			else:
				te = self.params[1] * 1e12
			rex = self.params[2] * (1e-8 * self.mf.data.frq[0])**2
			print "S2: " + `s2` + " te: " + `te` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
			self.mf.results.write("%-30s" % `s2`)
			self.mf.results.write("%-30s" % `te`)
			self.mf.results.write("%-30s" % `rex`)
		elif match('m5', self.mf.data.model):
			s2f = self.params[0]
			s2s = self.params[1]
			if self.scaling_flag:
				ts = self.params[2] * 1e12 / self.c
			else:
				ts = self.params[2] * 1e12
			print "S2f: " + `s2f` + " S2s: " + `s2s` + " ts: " + `ts` + " Chi2: " + `self.chi2`
			self.mf.results.write("%-30s" % `s2f`)
			self.mf.results.write("%-30s" % `s2s`)
			self.mf.results.write("%-30s" % `ts`)
		self.mf.results.write("%-30s" % `self.chi2`)
		self.mf.results.write("%-15s" % `self.iter_count`)
		self.mf.results.write("%-15s" % `self.f_count`)
		self.mf.results.write("%-15s" % `self.g_count`)
		self.mf.results.write("%-15s" % `self.h_count`)
		if self.warning:
			self.mf.results.write("%-30s\n" % `self.warning`)
		else:
			self.mf.results.write("\n")
