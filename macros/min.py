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


	def get_relax_data(self):
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
#			self.data, self.errors = self.get_data()
#			if self.data == None:
#				continue
#			self.function_ops = (self.relax.data.diff_type, self.relax.data.diff_params, self.model, self.data, self.errors)
#			self.params = self.relax.data.params[self.model_index][self.res]
#			print "self.data: " + `self.data`
#			print "self.errors: " + `self.errors`
#			print "self.params: " + `self.params`
#			print "self.function_ops: " + `self.function_ops`


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

		# Set up the minimisation specific options.
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

			# Setup the specific options for the tuple self.function_ops
			if match('mf', self.relax.data.equations[self.model_index]):
				self.functions_ops = self.setup_relax_data()
				if self.function_ops == None:
					continue
			else:
				print "Function options cannot be created."
				return

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

		print "\n[ Done ]\n\n"


	def minimisation_init(self):
		"Set up the minimisation specific options."

		if match('^[Nn]ewton$', self.min_algor):
			if self.min_options == None:
				self.min_options = 'More Thuente'
