from math import pi
from Numeric import Float64, array, zeros
from os import listdir, mkdir, remove
from re import match

#from common_ops import common_ops
from functions.mf_functions import mf_functions
from functions.mf_trans_functions import mf_trans_functions


class min:
	def __init__(self, relax):
		"Class containing functions specific to model-free analysis."

		self.relax = relax


	def old_crap(self):
		# Set the function, gradient, and hessian functions.
		if self.scaling_flag:
			self.functions = mf_trans_functions(self.relax)
			func = self.functions.chi2
			dfunc = self.functions.dchi2
			d2func = self.functions.d2chi2
		else:
			self.functions = mf_functions(self.relax)
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


	def calc_constants(self):
		"""Calculate the dipolar and CSA constants.

		Dipolar constants
		~~~~~~~~~~~~~~~~~
			      1   / mu0  \ 2  (gH.gN.h_bar)**2
			d  =  - . | ---- |  . ----------------
			      4   \ 4.pi /         <r**6>


			         3   / mu0  \ 2  (gH.gN.h_bar)**2
			d'  =  - - . | ---- |  . ----------------
			         2   \ 4.pi /         <r**7>


			       21   / mu0  \ 2  (gH.gN.h_bar)**2
			d"  =  -- . | ---- |  . ----------------
			       2    \ 4.pi /         <r**8>


		CSA constants
		~~~~~~~~~~~~~
			      (wN.csa)**2
			c  =  -----------
			           3


			       2.wN**2.csa
			c'  =  -----------
			            3


			       2.wN**2
			c"  =  -------
			          3

		"""

		# Dipolar constants.
		self.relax.data.dipole_const = zeros(len(self.relax.data.bond_length), Float64)
		self.relax.data.dipole_prime = zeros(len(self.relax.data.bond_length), Float64)
		self.relax.data.dipole_2prime = zeros(len(self.relax.data.bond_length), Float64)
		for i in range(len(self.relax.data.bond_length)):
			temp = ((self.relax.data.mu0 / (4.0*pi)) * self.relax.data.h_bar * self.relax.data.gh * self.relax.data.gx) ** 2
			self.relax.data.dipole_const[i] = 0.25 * temp * self.relax.data.bond_length[i][0]**-6
			self.relax.data.dipole_prime[i] = -1.5 * temp * self.relax.data.bond_length[i][0]**-7
			self.relax.data.dipole_2prime[i] = 10.5 * temp * self.relax.data.bond_length[i][0]**-8

		# CSA constants.
		self.relax.data.csa_const = zeros((self.relax.data.num_frq, len(self.relax.data.csa)), Float64)
		self.relax.data.csa_prime = zeros((self.relax.data.num_frq, len(self.relax.data.csa)), Float64)
		self.relax.data.csa_2prime = zeros((self.relax.data.num_frq, len(self.relax.data.csa)), Float64)
		for i in range(self.relax.data.num_frq):
			for j in range(len(self.relax.data.csa)):
				temp = self.relax.data.frq_sqrd_list[i, 1] / 3.0
				self.relax.data.csa_const[i, j] = temp * self.relax.data.csa[j][0]**2
				self.relax.data.csa_prime[i, j] = 2.0 * temp * self.relax.data.csa[j][0]
				self.relax.data.csa_2prime[i, j] = 2.0 * temp


	def calc_frq_list(self):
		"Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation."

		self.relax.data.frq_list = zeros((self.relax.data.num_frq, 5), Float64)
		for i in range(self.relax.data.num_frq):
			frqH = 2.0 * pi * self.relax.data.frq[i]
			frqX = frqH * (self.relax.data.gx / self.relax.data.gh)
			self.relax.data.frq_list[i, 1] = frqX
			self.relax.data.frq_list[i, 2] = frqH - frqX
			self.relax.data.frq_list[i, 3] = frqH
			self.relax.data.frq_list[i, 4] = frqH + frqX

		self.relax.data.frq_sqrd_list = self.relax.data.frq_list ** 2


	def find_model_index(self):
		"""Function to find the index of the model.

		If the model does not exist in self.relax.data.models, 'None' is returned, otherwise the index is returned.
		"""

		# See if the data structure exists.
		try:
			self.relax.data.models
		except AttributeError:
			return None

		# Test if the model is within the data structure.
		for i in range(len(self.relax.data.models)):
			if self.model == self.relax.data.models[i]:
				return i

		return None


	def function_init(self):
		"Initialise the functions used in the minimisation."

		if match('m[12345]', self.model):
			funcs = mf_functions(self.relax)
			self.func = funcs.chi2
			self.dfunc = funcs.dchi2
			self.d2func = funcs.d2chi2
			if match('[Ll][Mm]$', self.min_algor) or match('[Ll]evenburg-[Mm]arquardt$', self.min_algor):
				self.min_options.append(mf_functions.lm_dri)


	def get_data(self):
		"""Extract the data from self.relax.data.relax_data

		If any data is missing, None will be returned.
		"""

		data = zeros(self.relax.data.num_ri, Float64)
		errors = zeros(self.relax.data.num_ri, Float64)

		for i in range(self.relax.data.num_ri):
			if self.relax.data.relax_data[i][self.res, 2] == 0.0:
				return None, None
			data[i] = self.relax.data.relax_data[i][self.res, 0]
			errors[i] = self.relax.data.relax_data[i][self.res, 1]

		return data, errors


	def init_fixed_params(self):
		"""Fix the inital model-free parameter values.

		The function needs to be modified so the user can specify the fixed values.
		"""

		if len(self.min_options) == 0:
			if match('m1', self.model):
				params = array([0.5], Float64)
			elif match('m2', self.model):
				if self.scaling_flag:
					params = array([0.5, 100.0 * 1e-12 * self.c], Float64)
				else:
					params = array([0.5, 100.0 * 1e-12], Float64)
			elif match('m3', self.model):
				params = array([0.5, 0.0], Float64)
			elif match('m4', self.model):
				if self.scaling_flag:
					params = array([0.5, 0.0, 100.0 * 1e-12 * self.c], Float64)
				else:
					params = array([0.5, 0.0, 100.0 * 1e-12], Float64)
			elif match('m5', self.model):
				if self.scaling_flag:
					params = array([0.5, 0.5, 100.0 * 1e-12 * self.c], Float64)
				else:
					params = array([0.5, 0.5, 100.0 * 1e-12], Float64)

		elif len(self.min_options) == len(self.relax.data.model_parameters[self.model_index]):
			print "aaa"
		else:
			sys.exit()
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


	def min(self, model=None, min_algor=None, min_options=None, min_debug=1, scaling_flag=0, chi2_tol=1e-15, max_iterations=5000, overwrite_flag=0):
		"Minimisation macro."

		# Arguments.
		self.model = model
		if not self.model:
			print "No model is given."
			return
		self.min_algor = min_algor
		if not self.min_algor:
			print "The minimisation algorithm has not been specified."
			return
		self.min_options = min_options
		self.relax.min_debug = min_debug
		self.scaling_flag = scaling_flag
		self.chi2_tol = chi2_tol
		self.max_iterations = max_iterations
		self.overwrite_flag = overwrite_flag

		# Find the index of the model.
		self.model_index = self.find_model_index()
		if self.model_index == None:
			print "The model '" + self.model + "' has not been created yet."
			return

		# Function initialisation.
		self.function_init()

		# Create the directory and files for output.
		if not self.output_init(): return

		# Set up the minimisation specific things.
		self.minimisation_init()

		# Main iterative loop.
		for self.res in range(len(self.relax.data.seq)):
			if self.relax.min_debug >= 1:
				print "\n\n<<< Fitting to residue: " + `self.relax.data.seq[self.res][0]` + " " + self.relax.data.seq[self.res][1] + " >>>"
			else:
				print "Residue: " + `self.relax.data.seq[self.res][0]` + " " + self.relax.data.seq[self.res][1]

			# Initialise the iteration counter and function, gradient, and hessian call counters.
			self.iter_count = 0
			self.f_count = 0
			self.g_count = 0
			self.h_count = 0

			# Initialise the relaxation data and error data structures.
			self.data, self.errors = self.get_data()
			if self.data == None:
				continue
			self.function_ops = (self.relax.data.diff_type, self.relax.data.diff_params, self.model, self.data, self.errors)
			self.params = self.relax.data.params[self.model_index][self.res]
			print "self.data: " + `self.data`
			print "self.errors: " + `self.errors`
			print "self.params: " + `self.params`
			print "self.function_ops: " + `self.function_ops`

			# Minimisation.
			results = self.relax.minimise(self.func, dfunc=self.dfunc, d2func=self.d2func, args=self.function_ops, x0=self.params, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.chi2_tol, maxiter=self.max_iterations, full_output=1, print_flag=self.relax.min_debug)
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


	def minimisation_init(self):
		"Set up the minimisation specific options."

		if match('^[Nn]ewton$', self.min_algor):
			if self.min_options == None:
				self.min_options = 'More Thuente'


	def output_init(self):
		"""Create the directories and files for output.

		The directory with the name of the model will be created.
		The results will be placed in the file 'results' in the model directory.
		"""

		try:
			mkdir(self.model)
		except OSError:
			if self.overwrite_flag:
				files = listdir(self.model)
				for file in files:
					path = self.model + "/" + file
					remove(path)
			else:
				print "The directory ./" + self.model + " already exists."
				print "To overwrite, set the overwrite flag to 1."
				return 0

		self.relax.results = open(self.model + '/results', 'w')
		self.print_header()
		return 1


	def print_header(self):
		self.relax.results.write("%-5s" % "Num")
		self.relax.results.write("%-6s" % "Name")
		if match('m1', self.model):
			self.relax.results.write("%-30s" % "S2")
		elif match('m2', self.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % "te (ps)")
		elif match('m3', self.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
		elif match('m4', self.model):
			self.relax.results.write("%-30s" % "S2")
			self.relax.results.write("%-30s" % "te (ps)")
			self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
		elif match('m5', self.model):
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
		self.relax.results.write("%-5s" % self.relax.data.seq[self.res][0])
		self.relax.results.write("%-6s" % self.relax.data.seq[self.res][1])
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
