from math import pi
from Numeric import Float64, array, zeros
from re import match

from functions.mf import mf


class min:
	def __init__(self, relax):
		"Class containing functions specific to model-free analysis."

		self.relax = relax


	def fixed(self, model, values=None, print_flag=1):
		"""Macro to fix the initial parameter values.

		Arguments
		~~~~~~~~~

		model:		The name of the model.
		values:		An array of numbers of length equal to the number of parameters in
			the model.
		print_flag:	(so is this)


		Examples
		~~~~~~~~

		This command will fix the parameter values of the model 'm2', which is the original
		model-free equation with parameters [S2, te], before minimisation to the preselected
		values of this macro.

		relax> fixed('m2')


		This command will do the same except the S2 and te values will be set to one and ten
		ps respectively.

		relax> fixed('m2', [1.0, 10 * 10e-12])
		relax> fixed('m2', values = [1.0, 10 * 10e-12])


		FIN
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

		# The debugging flag.
		if type(print_flag) != int:
			print "The print_flag argument must be an integer."
			return
		else:
			self.print_flag = print_flag

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
						self.min_options[i] = 10.0 * 1e-12

					# S2s.
					elif match('S2s', self.relax.data.param_types[self.model][i]):
						self.min_options[i] = 0.5

					# ts.
					elif match('ts', self.relax.data.param_types[self.model][i]):
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

			# Unknown equation type.
			else:
				print "The equation " + `self.relax.data.equations[self.model]` + " has not been coded into the fixed parameter macro."
				return

		# Diagonal scaling.
		if self.relax.data.scaling.has_key(self.model):
			self.min_options = self.min_options / self.relax.data.scaling[self.model][0]

		# Setup values used in the main iterative loop.
		self.min_algor = 'fixed'
		self.func_tol = 0.0
		self.max_iterations = 0

		# Main iterative loop.
		self.main_loop()


	def grid_search(self, model, lower=None, upper=None, inc=21, print_flag=1):
		"""

		Generate the data structure of model-free grid options for the grid search.


		FIN
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


		# The debugging flag.
		if type(print_flag) != int:
			print "The print_flag argument must be an integer."
			return
		else:
			self.print_flag = print_flag

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
					self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# Rex.
				elif match('Rex', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2])

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
					self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# S2f.
				elif match('S2s', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 1.0])

				# tf.
				elif match('ts', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 10000.0 * 1e-12])

				# Rex.
				elif match('Rex', self.relax.data.param_types[self.model][i]):
					self.min_options.append([self.inc[i], 0.0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2])

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

		# Unknown equation type.
		else:
			print "The equation " + `self.relax.data.equations[self.model]` + " has not been coded into the grid search macro."
			return

		# Diagonal scaling.
		if self.relax.data.scaling.has_key(self.model):
			for i in range(len(self.min_options)):
				self.min_options[i][1] = self.min_options[i][1] / self.relax.data.scaling[self.model][0][i]
				self.min_options[i][2] = self.min_options[i][2] / self.relax.data.scaling[self.model][0][i]

		# Set the lower and upper bounds if these are supplied.
		for i in range(len(self.relax.data.param_types[self.model])):
			if not self.lower[i] == None:
				self.min_options[i][1] = self.lower[i]
			if not self.upper[i] == None:
				self.min_options[i][2] = self.upper[i]

		# Setup values used in the main iterative loop.
		self.min_algor = 'grid'
		self.func_tol = 0.0
		self.max_iterations = 0

		# Main iterative loop.
		self.main_loop()


	def main_loop(self):
		"The main iterative loop which loops over the residues."

		try:
			self.constraints
		except AttributeError:
			self.constraints = 0

		for self.res in range(len(self.relax.data.seq)):
			if self.print_flag >= 1:
				if self.print_flag >= 2:
					print "\n\n"
				string = "Fitting to residue: " + `self.relax.data.seq[self.res][0]` + " " + self.relax.data.seq[self.res][1]
				print string
				string2 = ""
				for i in range(len(string)):
					string2 = string2 + "~"
				print string2
			else:
				print "Residue: " + `self.relax.data.seq[self.res][0]` + " " + self.relax.data.seq[self.res][1]

			# Initialise the iteration counter and function, gradient, and Hessian call counters.
			self.iter_count = 0
			self.f_count = 0
			self.g_count = 0
			self.h_count = 0

			# Diagonal scaling.
			scaling_vector = None
			if self.relax.data.scaling.has_key(self.model):
				scaling_vector = self.relax.data.scaling[self.model][self.res]

			# Setup the function specific stuff.
			if match('mf', self.relax.data.equations[self.model]):
				# If any data is missing jump to the next residue.
				data = zeros(self.relax.data.num_ri, Float64)
				errors = zeros(self.relax.data.num_ri, Float64)
				for i in range(self.relax.data.num_ri):
					if self.relax.data.relax_data[i][self.res, 2] == 0.0:
						continue
					data[i] = self.relax.data.relax_data[i][self.res, 0]
					errors[i] = self.relax.data.relax_data[i][self.res, 1]
				self.function_ops = ()

				# Initialise the functions used in the minimisation.
				self.mf = mf(self.relax, equation=self.relax.data.equations[self.model], param_types=self.relax.data.param_types[self.model], init_params=self.relax.data.params[self.model][self.res], relax_data=data, errors=errors, bond_length=self.relax.data.bond_length[self.res][0], csa=self.relax.data.csa[self.res][0], diff_type=self.relax.data.diff_type, diff_params=self.relax.data.diff_params, scaling_vector=scaling_vector)

				# Levenberg-Marquardt minimisation.
				if match('[Ll][Mm]$', self.min_algor) or match('[Ll]evenburg-[Mm]arquardt$', self.min_algor):
					self.min_options = self.min_options + (self.mf.lm_dri, errors)
				# Levenberg-Marquardt minimisation with constraints.
				elif self.constraints == 1 and (match('[Ll][Mm]$', self.min_options[0]) or match('[Ll]evenburg-[Mm]arquardt$', self.min_options[0])):
					self.min_options = self.min_options + (self.mf.lm_dri, errors)

			# Minimisation.
			results = self.relax.minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=self.relax.data.params[self.model][self.res], min_algor=self.min_algor, min_options=self.min_options, func_tol=self.func_tol, maxiter=self.max_iterations, full_output=1, print_flag=self.print_flag)
			if results == None:
				return
			self.params, self.func, iter, fc, gc, hc, self.warning = results
			self.iter_count = self.iter_count + iter
			self.f_count = self.f_count + fc
			self.g_count = self.g_count + gc
			self.h_count = self.h_count + hc

			self.relax.data.params[self.model][self.res] = self.params

			# Write the results to file.
			# To do.

		print "\n[ Done ]\n\n"


	def minimise(self, *args, **keywords):
		"""Minimisation macro.

		The arguments specify the minimiser to use as well as the minimisation options.

		The following keywords can be supplied, any others will be ignored.
			model - a string specifying which model to minimise (this must be given).
			func_tol - the function tolerance between iterations, used to terminate
			   minisation.  The default value is 1e-25.
			max_iter - the maximum number of iterations.  The default value is 1e7.
			constraints - a flag specifying whether the parameters should be
			   constrained.  The default is to turn constraints on (constraints=1).
			print_flag - the amount of information to print to screen.  Zero corresponds
			   to minimal output, one is intermediate output, while two is maximal
			   output.  The default value is 1.


		FIN
		"""

		# Minimization algorithm.
		if len(args) == 0:
			print "The minimisation algorithm has not been specified."
			return
		self.min_algor = args[0]

		# Minimization options.
		self.min_options = args[1:]

		# Test for invalid keywords.
		valid_keywords = ['model', 'func_tol', 'max_iterations', 'max_iter', 'constraints', 'print_flag']
		for key in keywords:
			valid = 0
			for valid_key in valid_keywords:
				if key == valid_key:
					valid = 1
			if not valid:
				print "The keyword " + `key` + " is invalid."
				return

		# The model keyword.
		if keywords.has_key('model'):
			self.model = keywords['model']
			if type(self.model) != str:
				print "The model argument " + `self.model` + " must be a string."
				return
		else:
			print "No model has been given."
			return
		# self.res causing problems here!
		#if len(self.relax.data.params[self.model][self.res]) == 0:
		#	print "The minimisation of a zero parameter model is not allowed."
		#	return
		if not self.relax.data.equations.has_key(self.model):   # Find the index of the model.
			print "The model '" + self.model + "' has not been created yet."
			return

		# The function tolerance value.
		if keywords.has_key('func_tol'):
			self.func_tol = keywords['func_tol']
		else:
			self.func_tol = 1e-25

		# The maximum number of iterations.
		if keywords.has_key('max_iterations'):
			self.max_iterations = keywords['max_iterations']
		elif keywords.has_key('max_iter'):
			self.max_iterations = keywords['max_iter']
		else:
			self.max_iterations = 10000000

		# Constraint flag.
		if keywords.has_key('constraints'):
			self.constraints = keywords['constraints']
		else:
			self.constraints = 1
		if self.constraints == 1:
			self.min_algor = 'Method of Multipliers'
			self.min_options = args
		elif self.constraints != 0:
			print "The constraints flag (constraints=" + `self.constraints` + ") must be either 0 or 1."
			return

		# Print options.
		if keywords.has_key('print_flag'):
			self.print_flag = keywords['print_flag']
		else:
			self.print_flag = 1

		# Main iterative loop.
		self.main_loop()
