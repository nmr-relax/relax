from math import pi
from Numeric import Float64, array, zeros
from os import listdir, mkdir, remove
from re import match

from functions.mf import mf


class min:
	def __init__(self, relax):
		"Class containing functions specific to model-free analysis."

		self.relax = relax


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


	def min(self, model=None, min_algor=None, min_options=None, min_debug=1, scaling_flag=0, chi2_tol=1e-15, max_iterations=5000):
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

		# Find the index of the model.
		self.model_index = self.find_model_index()
		if self.model_index == None:
			print "The model '" + self.model + "' has not been created yet."
			return

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

			# Setup the function specific stuff.  If None or 0 is returned by self.setup_data, skip to the next residue.
			if not self.setup_data():
				continue

			# Minimisation.
			results = self.relax.minimise(self.func, dfunc=self.dfunc, d2func=self.d2func, args=self.function_ops, x0=self.params, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.chi2_tol, maxiter=self.max_iterations, full_output=1, print_flag=self.relax.min_debug)
			self.params, self.chi2, iter, fc, gc, hc, self.warning = results
			self.iter_count = self.iter_count + iter
			self.f_count = self.f_count + fc
			self.g_count = self.g_count + gc
			self.h_count = self.h_count + hc

			self.relax.data.params[self.res] = self.params

			if self.relax.min_debug:
				print "\n\n<<< Finished minimiser >>>"

			# Write the results to file.

		print "\n[ Done ]\n\n"


	def minimisation_init(self):
		"Set up the minimisation specific options."

		if match('^[Bb][Ff][Gg][Ss]$', self.min_algor) or match('^[Nn]ewton$', self.min_algor):
			if self.min_options == None:
				self.min_options = 'More Thuente'


	def setup_data(self):
		"""Extract the data from self.relax.data.relax_data

		If any data is missing, None will be returned which signals to the main iteration loop to jump to the next residue.
		"""

		if match('mf', self.relax.data.equations[self.model_index]):
			self.data = zeros(self.relax.data.num_ri, Float64)
			self.errors = zeros(self.relax.data.num_ri, Float64)

			for i in range(self.relax.data.num_ri):
				if self.relax.data.relax_data[i][self.res, 2] == 0.0:
					return None
				self.data[i] = self.relax.data.relax_data[i][self.res, 0]
				self.errors[i] = self.relax.data.relax_data[i][self.res, 1]

			self.function_ops = ()
			self.params = self.relax.data.params[self.model_index][self.res]

			# Initialise the functions used in the minimisation.
			self.mf = mf(self.relax, equation=self.relax.data.equations[self.model_index], param_types=self.relax.data.param_types[self.model_index], relax_data=self.data, errors=self.errors, bond_length=self.relax.data.bond_length[self.res][0], csa=self.relax.data.csa[self.res][0], diff_type=self.relax.data.diff_type, diff_params=self.relax.data.diff_params)
			self.func = self.mf.func
			self.dfunc = self.mf.dfunc
			self.d2func = self.mf.d2func
			if match('[Ll][Mm]$', self.min_algor) or match('[Ll]evenburg-[Mm]arquardt$', self.min_algor):
				self.min_options.append(self.mf.lm_dri)

		return 1


