from Numeric import Float64, zeros

from generic_functions import generic_functions


class mf_model(generic_functions):
	def __init__(self, relax):
		"Class for holding the preset model-free model macros."

		self.relax = relax


	def create(self, model=None, equation=None, param_types=None):
		"""Macro to create a model-free model.

		Arguments
		~~~~~~~~~

		model:		The name of the model-free model
		equation:	The model-free equation to use.  To select the original model-free equation set the equation to 'mf_orig'.
			To select the extended model-free equation set the equation to 'mf_ext'.
		param_type:	The parameters of the model.


		The following parameters are accepted for the original model-free equation:
			S2:		The square of the generalised order parameter.
			te:		The effective correlation time.
		The following parameters are accepted for the extended model-free equation:
			S2f:		The square of the generalised order parameter of the faster motion.
			tf:		The effective correlation time of the faster motion.
			S2s:		The square of the generalised order parameter of the slower motion.
			ts:		The effective correlation time of the slower motion.
		The following parameters are accepted for both the original and extended equations:
			Rex:		The chemical exchange relaxation.
			Bond length:	The average bond length <r>.
			CSA:		The chemical shift anisotropy.


		Examples
		~~~~~~~~

		The following commands will create the model-free model 'm1' which is based on the the original model-free equation and contains
		the single parameter 'S2'

		>>> mf_model_create('m1', 'mf_orig', ['S2'])
		>>> mf_model_create(model='m1', param_types=['S2'], equation='mf_orig')


		The following commands will create the model-free model 'large_model' which is based on the the extended model-free equation
		and contains the seven parameters 'S2f', 'tf', 'S2s', 'ts', 'Rex', 'CSA', 'Bond length'.

		>>> mf_model_create('large_model', 'mf_ext', ['S2f', 'tf', 'S2s', 'ts', 'Rex', 'CSA', 'Bond length'])
		>>> mf_model_create(model='large_model', param_types=['S2f', 'tf', 'S2s', 'ts', 'Rex', 'CSA', 'Bond length'], equation='mf_ext')
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


	def select(self, model):
		"""Macro for the selection of a preset model-free model.

		The preset models are:
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

		# Update the data structures.
		self.data_update()
