from math import pi
from Numeric import Float64, array, zeros
from os import listdir, mkdir, remove
from re import match

from functions.mf import mf


class min:
	def __init__(self, relax):
		"Class containing functions specific to model-free analysis."

		self.relax = relax


	def fixed(self, model, values=None, scaling_flag=0, min_debug=1):
		"""Macro to fix the initial parameter values.

		Arguments
		~~~~~~~~~

		model:		The name of the model.
		values:		An array of numbers of length equal to the number of parameters in the model.
		scaling_flag:	(This is temporary)
		min_debug:	(so is this)


		Examples
		~~~~~~~~

		This command will fix the parameter values of the model 'm2', which is the original model-free
		equation with parameters [S2, te], before minimisation to the preselected values of this macro.

		>>> fixed('m2')


		This command will do the same except the S2 and te values will be set to one and ten ps respectively.

		>>> fixed('m2', [1.0, 10 * 10e-12])
		>>> fixed('m2', values = [1.0, 10 * 10e-12])

		"""

		# The model argument.
		self.model = model
		if type(self.model) != str:
			print "The model argument " + `self.model` + " must be a string."
			return

		# Find the index of the model.
		if not self.relax.data.equations.has_key(self.model):
			print "The model '" + self.model + "' has not been created yet."
			return

		# User defined values.
		self.values = values
		if not self.values == None:
			if type(self.values) == list:
				if len(self.values) != len(self.relax.data.param_types[self.model]):
					print "The argument 'values' must be an array of length equal to the number of parameters in the model."
					print "Number of parameters = " + `len(self.relax.data.param_types[self.model])`
					print "Length of 'values' = " + `len(self.values)`
					return
				for i in range(len(self.values)):
					if type(self.values[i]) != float and type(self.values[i]) != int:
						print "The argument 'values' must be an array of numbers."
						return
			else:
				print "The argument 'values' must be an array of numbers."
				return

		# The scaling_flag.
		self.scaling_flag = scaling_flag
		if type(self.scaling_flag) != int:
			print "The scaling flag argument must be an integer."
			return

		# The debugging flag.
		if type(min_debug) != int:
			print "The min_debug argument must be an integer."
			return
		else:
			self.relax.min_debug = min_debug

		# Setup the fixed parameter options.
		if self.values:
			# User supplied values.
			self.min_options = array(self.values)
		else:
			# Fixed values.
			self.min_options = zeros(len(self.relax.data.param_types[self.model]), Float64)

			# The original model-free equations.
			if match('mf_orig', self.relax.data.equations[self.model]):
				for i in range(len(self.relax.data.param_types[self.model])):
					# S2.
					if match('S2', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.5

					# te.
					elif match('te', self.relax.data.param_types[self.model][i]):
						if self.scaling_flag:
							self.min_options[i] = 100.0 * 1e-12 * self.c
						else:
							self.min_options[i] = 100.0 * 1e-12

					# Rex.
					elif match('Rex', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.0

					# Bond length.
					elif match('Bond length', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 1.02 * 1e-10

					# CSA.
					elif match('CSA', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = -170 * 1e-6

					# Unknown parameter.
					else:
						print "Unknown parameter '" + self.relax.data.param_types[self.model][i] + "' for the original model-free equation."
						return

			# The extended model-free equations.
			elif match('mf_ext', self.relax.data.equations[self.model]):
				for i in range(len(self.relax.data.param_types[self.model])):
					# S2f.
					if match('S2f', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.5

					# tf.
					elif match('tf', self.relax.data.param_types[self.model][i]):
						if self.scaling_flag:
							self.min_options[i] = 10.0 * 1e-12 * self.c
						else:
							self.min_options[i] = 10.0 * 1e-12

					# S2s.
					elif match('S2s', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.5

					# ts.
					elif match('ts', self.relax.data.param_types[self.model][i]):
						if self.scaling_flag:
							self.min_options[i] = 1000.0 * 1e-12 * self.c
						else:
							self.min_options[i] = 1000.0 * 1e-12

					# Rex.
					elif match('Rex', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.0

					# Bond length.
					elif match('Bond length', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 1.02 * 1e-10

					# CSA.
					elif match('CSA', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = -170 * 1e-6

					# Unknown parameter.
					else:
						print "Unknown parameter '" + self.relax.data.param_types[self.model][i] + "' for the extended model-free equation."
						return

			# Unknown eqation type.
			else:
				print "The equation " + `self.relax.data.equations[self.model]` + " has not been coded into the fixed parameter macro."
				return

		# Setup values used in the main iterative loop.
		self.min_algor = 'fixed'
		self.chi2_tol = 0.0
		self.max_iterations = 0

		# Main iterative loop.
		self.main_loop()


	def grid_search(self, model, lower=None, upper=None, inc=21, scaling_flag=0, min_debug=1):
		"""

		Generate the data structure of model-free grid options for the grid search.
		"""

		# The model argument.
		self.model = model
		if type(self.model) != str:
			print "The model argument " + `self.model` + " must be a string."
			return

		# Find the index of the model.
		if not self.relax.data.equations.has_key(self.model):
			print "The model '" + self.model + "' has not been created yet."
			return

		# The lower bounds.
		self.lower = lower
		if self.lower:
			bad_arg = 0
			if len(self.lower) != len(self.relax.data.param_types[self.model]):
				bad_arg = 1
			for i in range(len(self.lower)):
				if type(self.lower[i]) != float and type(self.lower[i]) != int:
					bad_arg = 1
			if bad_arg:
				print "The argument 'lower' must be an array of numbers of length equal to the number of parameters in the model."
				return
		else:
			self.lower = []
			for i in range(len(self.relax.data.param_types[self.model])):
				self.lower.append(None)

		# The upper bounds.
		self.upper = upper
		if self.upper:
			bad_arg = 0
			if len(self.upper) != len(self.relax.data.param_types[self.model]):
				bad_arg = 1
			for i in range(len(self.upper)):
				if type(self.upper[i]) != float and type(self.upper[i]) != int:
					bad_arg = 1
			if bad_arg:
				print "The argument 'upper' must be an array of numbers of length equal to the number of parameters in the model."
				return
		else:
			self.upper = []
			for i in range(len(self.relax.data.param_types[self.model])):
				self.upper.append(None)

		# The incrementation value.
		bad_arg = 0
		if type(inc) != int and type(inc) != list:
			bad_arg = 1
		if type(inc) == list:
			if len(inc) != len(self.relax.data.param_types[self.model]):
				bad_arg = 1
			for i in range(len(inc)):
				if type(inc[i]) != int:
					bad_arg = 1
		if bad_arg:
			print "The argument 'inc' must be either an integer or an array of integers of length equal to the number of parameters in the model."
			return
		elif type(inc) == int:
			self.inc = []
			for i in range(len(self.relax.data.param_types[self.model])):
				self.inc.append(inc)
		else:
			self.inc = inc


		# The scaling_flag.
		self.scaling_flag = scaling_flag
		if type(self.scaling_flag) != int:
			print "The scaling flag argument must be an integer."
			return

		# The debugging flag.
		if type(min_debug) != int:
			print "The min_debug argument must be an integer."
			return
		else:
			self.relax.min_debug = min_debug

		# Setup the grid options.
		self.min_options = []

		# The original model-free equations.
		if match('mf_orig', self.relax.data.equations[self.model]):
			for i in range(len(self.relax.data.param_types[self.model])):
				# S2.
				if match('S2', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 1.0])

				# te.
				elif match('te', self.relax.data.param_types[self.model][i]):
					if self.scaling_flag:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12 * self.c])
					else:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# Rex.
				elif match('Rex', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 30.0 / (1e-8 * self.relax.data.frq[0])**2])

				# Bond length.
				elif match('Bond length', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 1.0 * 1e-10, 1.05 * 1e-10])

				# CSA.
				elif match('CSA', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], -120 * 1e-6, -200 * 1e-6])

				# Unknown parameter.
				else:
					print "Unknown parameter '" + self.relax.data.param_types[self.model][i] + "' for the original model-free equation."
					return

		# The extended model-free equations.
		elif match('mf_ext', self.relax.data.equations[self.model]):
			for i in range(len(self.relax.data.param_types[self.model])):
				# S2f.
				if match('S2f', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 1.0])

				# tf.
				elif match('tf', self.relax.data.param_types[self.model][i]):
					if self.scaling_flag:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12 * self.c])
					else:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# S2f.
				elif match('S2s', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 1.0])

				# tf.
				elif match('ts', self.relax.data.param_types[self.model][i]):
					if self.scaling_flag:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12 * self.c])
					else:
						self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# Rex.
				elif match('Rex', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 30.0 / (1e-8 * self.relax.data.frq[0])**2])

				# Bond length.
				elif match('Bond length', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 1.0 * 1e-10, 1.1 * 1e-10])

				# CSA.
				elif match('CSA', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], -120 * 1e-6, -200 * 1e-6])

				# Unknown parameter.
				else:
					print "Unknown parameter '" + self.relax.data.param_types[self.model][i] + "' for the extended model-free equation."
					return

		# Unknown eqation type.
		else:
			print "The equation " + `self.relax.data.equations[self.model]` + " has not been coded into the grid search macro."
			return

		# Set the lower and upper bounds if these are supplied.
		for i in range(len(self.relax.data.param_types[self.model])):
			if not self.lower[i] == None:
				self.min_options[i][1] = self.lower[i]
			if not self.upper[i] == None:
				self.min_options[i][2] = self.upper[i]

		# Setup values used in the main iterative loop.
		self.min_algor = 'grid'
		self.chi2_tol = 0.0
		self.max_iterations = 0

		# Main iterative loop.
		self.main_loop()


	def main_loop(self):
		"The main iterative loop which loops over the residues."

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

			self.relax.data.params[self.model][self.res] = self.params

			if self.relax.min_debug:
				print "\n\n<<< Finished minimiser >>>"

			# Write the results to file.

		print "\n[ Done ]\n\n"


	def minimise(self, model, min_algor=None, min_options=None, chi2_tol=1e-25, max_iterations=10000, scaling_flag=0, min_debug=1):
		"Minimisation macro."

		# The model argument.
		self.model = model
		if type(self.model) != str:
			print "The model argument " + `self.model` + " must be a string."
			return

		self.model = model

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
		if not self.relax.data.equations.has_key(self.model):
			print "The model '" + self.model + "' has not been created yet."
			return

		# Set up the minimisation specific options.
		# Line search methods.
		if match('^[Cc][Dd]$', self.min_algor) or match('^[Cc]oordinate[ _-][Dd]escent$', self.min_algor) or match('^[Ss][Dd]$', self.min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', self.min_algor) or match('^[Bb][Ff][Gg][Ss]$', self.min_algor) or match('^[Nn]ewton$', self.min_algor):
			if self.min_options == None:
				self.min_options = 'More Thuente'

		# Main iterative loop.
		self.main_loop()


	def setup_data(self):
		"""Extract the data from self.relax.data.relax_data

		If any data is missing, None will be returned which signals to the main iteration loop to jump to the next residue.
		"""

		if match('mf', self.relax.data.equations[self.model]):
			self.data = zeros(self.relax.data.num_ri, Float64)
			self.errors = zeros(self.relax.data.num_ri, Float64)

			for i in range(self.relax.data.num_ri):
				if self.relax.data.relax_data[i][self.res, 2] == 0.0:
					return None
				self.data[i] = self.relax.data.relax_data[i][self.res, 0]
				self.errors[i] = self.relax.data.relax_data[i][self.res, 1]

			self.function_ops = ()
			self.params = self.relax.data.params[self.model][self.res]

			# Initialise the functions used in the minimisation.
			self.mf = mf(self.relax, equation=self.relax.data.equations[self.model], param_types=self.relax.data.param_types[self.model], init_params=self.params, relax_data=self.data, errors=self.errors, bond_length=self.relax.data.bond_length[self.res][0], csa=self.relax.data.csa[self.res][0], diff_type=self.relax.data.diff_type, diff_params=self.relax.data.diff_params)
			self.func = self.mf.func
			self.dfunc = self.mf.dfunc
			self.d2func = self.mf.d2func
			if match('[Ll][Mm]$', self.min_algor) or match('[Ll]evenburg-[Mm]arquardt$', self.min_algor):
				self.min_options.append(self.mf.lm_dri)

		return 1


