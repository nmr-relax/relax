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


	def list(self):
		"Print the list of preset model-free models."

		print "'m1' => [S2]"
		print "'m2' => [S2, te]"
		print "'m3' => [S2, Rex]"
		print "'m4' => [S2, te, Rex]"
		print "'m5' => [S2f, S2s, ts]"


	def select(self, model):
		"Select the preset model-free model."

		# Test if sequence data is loaded.
		if not self.sequence_data_test(): return

		# Add the model.
		try:
			self.relax.data.models.append(model)
		except AttributeError:
			self.relax.data.models = [model]
			self.relax.data.equations = []
			self.relax.data.param_types = []
			self.relax.data.params = []
			self.relax.data.param_errors = []

		if model == 'm1':
			self.relax.data.equations.append('mf_orig')
			self.relax.data.param_types.append(['S2'])
		elif model == 'm2':
			self.relax.data.equations.append('mf_orig')
			self.relax.data.param_types.append(['S2', 'te'])
		elif model == 'm3':
			self.relax.data.equations.append('mf_orig')
			self.relax.data.param_types.append(['S2', 'Rex'])
		elif model == 'm4':
			self.relax.data.equations.append('mf_orig')
			self.relax.data.param_types.append(['S2', 'te', 'Rex'])
		elif model == 'm5':
			self.relax.data.equations.append('mf_ext')
			self.relax.data.param_types.append(['S2f', 'S2s', 'ts'])
		else:
			print "The model '" + model + "' is invalid."
			return


		# Create the params data structure.
		index = len(self.relax.data.models) - 1
		self.relax.data.params.append(zeros((len(self.relax.data.seq), len(self.relax.data.param_types[index])), Float64))
		self.relax.data.param_errors.append(zeros((len(self.relax.data.seq), len(self.relax.data.param_types[index])), Float64))
