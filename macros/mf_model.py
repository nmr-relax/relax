from Numeric import Float64, zeros

from generic_functions import generic_functions


class mf_model(generic_functions):
	def __init__(self, relax):
		"Class for holding the preset model-free model macros."

		self.relax = relax


	def create(self, name=None, equation=None, param_types=None):
		"Macro to create arbritary model-free models."

		if not name:
			print "Model-free model name not given."
			return
		elif not equation:
			print "Model-free equation type not selected."
			return
		elif not param_types:
			print "Model-free parameters not given."
			return
		elif not equation == 'mf_orig' or not equation == 'mf_ext':
			print "Model-free equation '" + equation + "' not supported."
			return

		# Add the model.
		try:
			self.relax.data.models.append(model)
			self.relax.data.equations.append(equation)
			self.relax.data.param_types.append(param_types)
			self.relax.data.params.append([])
		except AttributeError:
			self.relax.data.models = [model]
			self.relax.data.equations = [equation]
			self.relax.data.param_types = [param_types]
			self.relax.data.params = []


		# Create the params data structure.
		for i in range(len(self.relax.data.seq)):
			self.relax.data.params.append([None, None])


	def data_update(self):
		"Function for updating various data structures depending on the model selected."

		# Try to append the model name to the self.relax.data.models data structure.
		# If self.relax.data.models does not exist, initialise the equations, param_types, params, and param_errors data structures.
		try:
			self.relax.data.models.append(self.model)
		except AttributeError:
			self.relax.data.models = [self.model]
			self.relax.data.equations = []
			self.relax.data.param_types = []
			self.relax.data.params = []
			self.relax.data.param_errors = []

		# Update the equation and param_types data structures.
		self.relax.data.equations.append(self.equation)
		self.relax.data.param_types.append(self.types)

		# Create the params data structure.
		index = len(self.relax.data.models) - 1
		self.relax.data.params.append(zeros((len(self.relax.data.seq), len(self.relax.data.param_types[index])), Float64))
		self.relax.data.param_errors.append(zeros((len(self.relax.data.seq), len(self.relax.data.param_types[index])), Float64))


	def select(self, model):
		"""Macro for the selection of a preset model-free model.

		The preset models are:
			'm1'	=> [S2]
			'm2'	=> [S2, te]
			'm3'	=> [S2, Rex]
			'm4'	=> [S2, te, Rex]
			'm5'	=> [S2f, S2s, ts]
			'm6'	=> [S2f, tf, S2s, ts]
			'm7'	=> [S2f, S2s, ts, Rex]
			'm8'	=> [S2f, tf, S2s, ts, Rex]

			'm10'	=> [CSA]
			'm11'	=> [CSA, S2]
			'm12'	=> [CSA, S2, te]
			'm13'	=> [CSA, S2, Rex]
			'm14'	=> [CSA, S2, te, Rex]
			'm15'	=> [CSA, S2f, S2s, ts]
			'm16'	=> [CSA, S2f, tf, S2s, ts]
			'm17'	=> [CSA, S2f, S2s, ts, Rex]
			'm18'	=> [CSA, S2f, tf, S2s, ts, Rex]

			'm20'	=> [Bond length]
			'm21'	=> [Bond length, S2]
			'm22'	=> [Bond length, S2, te]
			'm23'	=> [Bond length, S2, Rex]
			'm24'	=> [Bond length, S2, te, Rex]
			'm25'	=> [Bond length, S2f, S2s, ts]
			'm26'	=> [Bond length, S2f, tf, S2s, ts]
			'm27'	=> [Bond length, S2f, S2s, ts, Rex]
			'm28'	=> [Bond length, S2f, tf, S2s, ts, Rex]

			'm30'	=> [Bond length, CSA]
			'm31'	=> [Bond length, CSA, S2]
			'm32'	=> [Bond length, CSA, S2, te]
			'm33'	=> [Bond length, CSA, S2, Rex]
			'm34'	=> [Bond length, CSA, S2, te, Rex]
			'm35'	=> [Bond length, CSA, S2f, S2s, ts]
			'm36'	=> [Bond length, CSA, S2f, tf, S2s, ts]
			'm37'	=> [Bond length, CSA, S2f, S2s, ts, Rex]
			'm38'	=> [Bond length, CSA, S2f, tf, S2s, ts, Rex]


		"""

		# Arguments.
		self.model = model

		# Test if sequence data is loaded.
		if not self.sequence_data_test(): return

		# Block 1.
		if model == 'm1':
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

		# Invalid models.
		else:
			print "The model '" + model + "' is invalid."
			return

		# Update the data structures.
		self.data_update()
