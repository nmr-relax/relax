from math import pi
from Numeric import Float64, ones, zeros
from re import match

from generic_functions import generic_functions


class skin:
	def __init__(self, relax):
		"""The class accessible to the interpreter.

		The purpose of this class is to hide the variables and functions found within the
		namespace of the macro class, found below, except for those required for interactive
		use.  This is an abstraction layer designed to avoid user confusion as none of the
		macro class data structures are accessible.  For more flexibility use the macro
		class directly.
		"""

		# Load the macro class into the namespace of this __init__ function.
		x = macro_class(relax)

		# Place references to the interactive functions within the namespace of this skin class.
		self.create = x.create
		self.select = x.select


class macro_class(generic_functions):
	def __init__(self, relax):
		"Class for holding the preset model-free model macros."

		self.relax = relax


	def create(self, model=None, equation=None, param_types=None, scaling=1):
		"""Macro to create a model-free model.

		Arguments
		~~~~~~~~~

		model:		The name of the model-free model
		equation:	The model-free equation.
		param_type:	The parameters of the model.


		Description
		~~~~~~~~~~~

		For selection of the model-free equation the string 'mf_orig' will select the
		original model-free equation while the string 'mf_ext' will select the extended
		model-free equation.

		The following parameters are accepted for the original model-free equation:
			S2:		The square of the generalised order parameter.
			te:		The effective correlation time.
		The following parameters are accepted for the extended model-free equation:
			S2f:		The square of the generalised order parameter of the faster
				motion.
			tf:		The effective correlation time of the faster motion.
			S2s:		The square of the generalised order parameter of the slower
				motion.
			ts:		The effective correlation time of the slower motion.
		The following parameters are accepted for both the original and extended equations:
			Rex:		The chemical exchange relaxation.
			Bond length:	The average bond length <r>.
			CSA:		The chemical shift anisotropy.


		Examples
		~~~~~~~~

		The following commands will create the model-free model 'm1' which is based on the
		original model-free equation and contains the single parameter 'S2'.

		relax> mf_model_create('m1', 'mf_orig', ['S2'])
		relax> mf_model_create(model='m1', param_types=['S2'], equation='mf_orig')


		The following commands will create the model-free model 'large_model' which is based
		on the the extended model-free equation and contains the seven parameters 'S2f',
		'tf', 'S2s', 'ts', 'Rex', 'CSA', 'Bond length'.

		relax> mf_model_create('large_model', 'mf_ext', ['S2f', 'tf', 'S2s', 'ts', 'Rex',
		'CSA', 'Bond length'])
		relax> mf_model_create(model='large_model', param_types=['S2f', 'tf', 'S2s', 'ts',
		'Rex', 'CSA', 'Bond length'], equation='mf_ext')


		FIN
		"""

		if not model or type(model) != str:
			print "Model-free model name is invalid."
			return
		elif not equation:
			print "Model-free equation type not selected."
			return
		elif not param_types:
			print "Model-free parameters not given."
			return
		elif not equation == 'mf_orig' and not equation == 'mf_ext':
			print "Model-free equation '" + equation + "' is not supported."
			return

		# Test if sequence data is loaded.
		if not len(self.relax.data.seq):
			print "Sequence data has to be loaded first."
			return

		# Arguments
		self.model = model
		self.equation = equation
		self.types = param_types

		# Test the scaling flag.
		if scaling == 0 or scaling == 1:
			self.scaling = scaling
		else:
			print "The scaling flag is set incorrectly."
			return

		# Test the parameter names.
		s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
		for i in range(len(self.types)):
			# Check if the parameter is a string.
			if type(self.types[i]) != str:
				print "The parameter " + `self.types[i]` + " is not a string."
				return

			# Test the parameter.
			invalid_param = 0
			if self.types[i] == 'S2':
				if self.equation == 'mf_ext' or s2:
					invalid_param = 1
				s2 = 1
			elif self.types[i] == 'te':
				if self.equation == 'mf_ext' or te:
					invalid_param = 1
				s2_flag = 0
				for j in range(len(self.types)):
					if self.types[j] == 'S2':
						s2_flag = 1
				if not s2_flag:
					invalid_param = 1
				te = 1
			elif self.types[i] == 'S2f':
				if self.equation == 'mf_orig' or s2f:
					invalid_param = 1
				s2f = 1
			elif self.types[i] == 'tf':
				if self.equation == 'mf_orig' or tf:
					invalid_param = 1
				s2f_flag = 0
				for j in range(len(self.types)):
					if self.types[j] == 'S2f':
						s2f_flag = 1
				if not s2f_flag:
					invalid_param = 1
				tf = 1
			elif self.types[i] == 'S2s':
				if self.equation == 'mf_orig' or s2s:
					invalid_param = 1
				s2s = 1
			elif self.types[i] == 'ts':
				if self.equation == 'mf_orig' or ts:
					invalid_param = 1
				s2s_flag = 0
				for j in range(len(self.types)):
					if self.types[j] == 'S2s':
						s2s_flag = 1
				if not s2s_flag:
					invalid_param = 1
				ts = 1
			elif self.types[i] == 'Rex':
				if rex:
					invalid_param = 1
				rex = 1
			elif self.types[i] == 'Bond length':
				if r:
					invalid_param = 1
				r = 1
			elif self.types[i] == 'CSA':
				if csa:
					invalid_param = 1
				csa = 1
			else:
				print "The parameter " + self.types[i] + " is not supported."
				return

			# The invalid parameter flag is set.
			if invalid_param:
				print "The parameter array " + `self.types` + " contains an invalid parameter or combination of parameters."
				return

		# Create the scaling vector.
		self.scaling_vector()

		# Update the data structures.
		self.data_update()


	def data_update(self):
		"Function for updating various data structures depending on the model selected."

		# Update the equation and param_types data structures.
		self.relax.data.equations[self.model] = self.equation
		self.relax.data.param_types[self.model] = self.types

		# Create the params data structure.
		self.relax.data.params[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)
		self.relax.data.param_errors[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)

		# Diagonal scaling.
		if self.scaling:
			self.relax.data.scaling[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)
			self.relax.data.scaling[self.model][:] = self.scale_vect


	def scaling_vector(self):
		"Function for creating the scaling vector."

		self.scale_vect = ones(len(self.types), Float64)
		for i in range(len(self.types)):
			# te, tf, and ts.
			if match('t', self.types[i]):
				self.scale_vect[i] = 1e-9
			elif self.types[i] == 'Rex':
				self.scale_vect[i] = 1.0 / (2.0 * pi * self.relax.data.frq[0]) ** 2
			elif self.types[i] == 'Bond length':
				self.scale_vect[i] = 1e-10
			elif self.types[i] == 'CSA':
				self.scale_vect[i] = 1e-4



	def select(self, model, scaling=1):
		"""Macro for the selection of a preset model-free model.

		Arguments
		~~~~~~~~~

		model:		The name of the preset model.
		scaling:	The diagonal scaling flag.


		Description
		~~~~~~~~~~~

		The preset model-free models are:
			'm0'	=> []
			'm1'	=> [S2]
			'm2'	=> [S2, te]
			'm3'	=> [S2, Rex]
			'm4'	=> [S2, te, Rex]
			'm5'	=> [S2f, S2s, ts]
			'm6'	=> [S2f, tf, S2s, ts]
			'm7'	=> [S2f, S2s, ts, Rex]
			'm8'	=> [S2f, tf, S2s, ts, Rex]
			'm9'	=> [Rex]

			'm10'	=> [CSA]
			'm11'	=> [CSA, S2]
			'm12'	=> [CSA, S2, te]
			'm13'	=> [CSA, S2, Rex]
			'm14'	=> [CSA, S2, te, Rex]
			'm15'	=> [CSA, S2f, S2s, ts]
			'm16'	=> [CSA, S2f, tf, S2s, ts]
			'm17'	=> [CSA, S2f, S2s, ts, Rex]
			'm18'	=> [CSA, S2f, tf, S2s, ts, Rex]
			'm19'	=> [CSA, Rex]

			'm20'	=> [Bond length]
			'm21'	=> [Bond length, S2]
			'm22'	=> [Bond length, S2, te]
			'm23'	=> [Bond length, S2, Rex]
			'm24'	=> [Bond length, S2, te, Rex]
			'm25'	=> [Bond length, S2f, S2s, ts]
			'm26'	=> [Bond length, S2f, tf, S2s, ts]
			'm27'	=> [Bond length, S2f, S2s, ts, Rex]
			'm28'	=> [Bond length, S2f, tf, S2s, ts, Rex]
			'm29'	=> [Bond length, CSA, Rex]

			'm30'	=> [Bond length, CSA]
			'm31'	=> [Bond length, CSA, S2]
			'm32'	=> [Bond length, CSA, S2, te]
			'm33'	=> [Bond length, CSA, S2, Rex]
			'm34'	=> [Bond length, CSA, S2, te, Rex]
			'm35'	=> [Bond length, CSA, S2f, S2s, ts]
			'm36'	=> [Bond length, CSA, S2f, tf, S2s, ts]
			'm37'	=> [Bond length, CSA, S2f, S2s, ts, Rex]
			'm38'	=> [Bond length, CSA, S2f, tf, S2s, ts, Rex]
			'm39'	=> [Bond length, CSA, Rex]

		Warning:  A few of the models in the thirties range fail when using standard R1, R2,
		and NOE relaxation data.


		Diagonal scaling.

		This is the scaling of parameter values with the intent of having the same order of
		magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
		Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10,
		1.055e-18] (Rex is divided by (2*pi*600,000,000)**2 to make it field strength
		independent).  The scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].
		By dividing the unscaled parameter vector by the scaling vector the scaled parameter
		vector is [0.5, 2.0, 15.0].  To revert to the original unscaled parameter vector,
		the scaled parameter vector and scaling vector are multiplied.  The reason for
		diagonal scaling is that certain minimisation techniques fail when the model is not
		properly scaled.


		Examples
		~~~~~~~~

		To pick model 'm1', run:

		relax> mf_model_select('m1')


		FIN
		"""

		# Arguments.
		self.model = model

		# Test if sequence data is loaded.
		if not len(self.relax.data.seq):
			print "Sequence data has to be loaded first."
			return

		# Test if the model already exists.
		if self.relax.data.equations.has_key(self.model):
			print "The model " + self.model + " already exists."
			return

		# Test the scaling flag.
		if scaling == 0 or scaling == 1:
			self.scaling = scaling
		else:
			print "The scaling flag is set incorrectly."
			return

		# Block 1.
		if model == 'm0':
			self.equation = 'mf_orig'
			self.types = []
		elif model == 'm1':
			self.equation = 'mf_orig'
			self.types = ['S2']
		elif model == 'm2':
			self.equation = 'mf_orig'
			self.types = ['S2', 'te']
		elif model == 'm3':
			self.equation = 'mf_orig'
			self.types = ['S2', 'Rex']
		elif model == 'm4':
			self.equation = 'mf_orig'
			self.types = ['S2', 'te', 'Rex']
		elif model == 'm5':
			self.equation = 'mf_ext'
			self.types = ['S2f', 'S2s', 'ts']
		elif model == 'm6':
			self.equation = 'mf_ext'
			self.types = ['S2f', 'tf', 'S2s', 'ts']
		elif model == 'm7':
			self.equation = 'mf_ext'
			self.types = ['S2f', 'S2s', 'ts', 'Rex']
		elif model == 'm8':
			self.equation = 'mf_ext'
			self.types = ['S2f', 'tf', 'S2s', 'ts', 'Rex']
		elif model == 'm9':
			self.equation = 'mf_orig'
			self.types = ['Rex']

		# Block 2.
		elif model == 'm10':
			self.equation = 'mf_orig'
			self.types = ['CSA']
		elif model == 'm11':
			self.equation = 'mf_orig'
			self.types = ['CSA', 'S2']
		elif model == 'm12':
			self.equation = 'mf_orig'
			self.types = ['CSA', 'S2', 'te']
		elif model == 'm13':
			self.equation = 'mf_orig'
			self.types = ['CSA', 'S2', 'Rex']
		elif model == 'm14':
			self.equation = 'mf_orig'
			self.types = ['CSA', 'S2', 'te', 'Rex']
		elif model == 'm15':
			self.equation = 'mf_ext'
			self.types = ['CSA', 'S2f', 'S2s', 'ts']
		elif model == 'm16':
			self.equation = 'mf_ext'
			self.types = ['CSA', 'S2f', 'tf', 'S2s', 'ts']
		elif model == 'm17':
			self.equation = 'mf_ext'
			self.types = ['CSA', 'S2f', 'S2s', 'ts', 'Rex']
		elif model == 'm18':
			self.equation = 'mf_ext'
			self.types = ['CSA', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
		elif model == 'm19':
			self.equation = 'mf_orig'
			self.types = ['CSA', 'Rex']

		# Block 3.
		elif model == 'm20':
			self.equation = 'mf_orig'
			self.types = ['Bond length']
		elif model == 'm21':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'S2']
		elif model == 'm22':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'S2', 'te']
		elif model == 'm23':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'S2', 'Rex']
		elif model == 'm24':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'S2', 'te', 'Rex']
		elif model == 'm25':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'S2f', 'S2s', 'ts']
		elif model == 'm26':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'S2f', 'tf', 'S2s', 'ts']
		elif model == 'm27':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'S2f', 'S2s', 'ts', 'Rex']
		elif model == 'm28':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
		elif model == 'm29':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'Rex']

		# Block 4.
		elif model == 'm30':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA']
		elif model == 'm31':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA', 'S2']
		elif model == 'm32':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA', 'S2', 'te']
		elif model == 'm33':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA', 'S2', 'Rex']
		elif model == 'm34':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA', 'S2', 'te', 'Rex']
		elif model == 'm35':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'CSA', 'S2f', 'S2s', 'ts']
		elif model == 'm36':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'CSA', 'S2f', 'tf', 'S2s', 'ts']
		elif model == 'm37':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'CSA', 'S2f', 'S2s', 'ts', 'Rex']
		elif model == 'm38':
			self.equation = 'mf_ext'
			self.types = ['Bond length', 'CSA', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
		elif model == 'm39':
			self.equation = 'mf_orig'
			self.types = ['Bond length', 'CSA', 'Rex']

		# Invalid models.
		else:
			print "The model '" + model + "' is invalid."
			return

		# Create the scaling vector.
		self.scaling_vector()

		# Update the data structures.
		self.data_update()
