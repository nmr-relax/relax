from functions.mf_functions import mf_functions
from generic_functions import generic_functions


class mf_model(generic_functions):
	def __init__(self, relax):
		"Class for holding the preset model-free model macros."

		self.relax = relax


	def create(self, name=None, equation=None, param_types=None):
		"Macro to create arbritary model-free models."

		print "Executing macro create_mf_model"

		if not name:
			print "Model-free model name not given."
			print "[ failed ]"
			return
		elif not equation:
			print "Model-free equation type not selected."
			print "[ failed ]"
			return
		elif not param_types:
			print "Model-free parameters not given."
			print "[ failed ]"
			return
		elif not equation == 'original' or not equation == 'extended':
			print "Model-free equation '" + equation + "' not supported."
			print "[ failed ]"
			return

		# Add the model.
		try:
			self.relax.data.mf_model.append(model)
			self.relax.data.mf_equation.append(equation)
			self.relax.data.mf_param_types.append(param_types)
			self.relax.data.mf_params.append([])
		except AttributeError:
			self.relax.data.mf_model = [model]
			self.relax.data.mf_equation = [equation]
			self.relax.data.mf_param_types = [param_types]
			self.relax.data.mf_params = []

		self.relax.data.func = mf_functions(self.relax)

		# Create the mf_params data structure.
		for i in range(len(self.relax.data.seq)):
			self.relax.data.mf_params.append([None, None])

		print "[ OK ]"


	def list(self):
		"Print the list of preset model-free models."

		print "Executing macro list_preset_mf_model"
		print "'m1' => [S2]"
		print "'m2' => [S2, te]"
		print "'m3' => [S2, Rex]"
		print "'m4' => [S2, te, Rex]"
		print "'m5' => [S2f, S2s, ts]"
		print "[ OK ]"


	def select(self, model):
		"Select the preset model-free model."

		print "Executing macro select_preset_mf_model"

		# Test if sequence data is loaded.
		if not self.sequence_data_test(): return

		# Add the model.
		try:
			self.relax.data.mf_model.append(model)
		except AttributeError:
			self.relax.data.mf_model = [model]
			self.relax.data.mf_equation = []
			self.relax.data.mf_param_types = []
			self.relax.data.mf_params = []

		if model == 'm1':
			self.relax.data.mf_equation.append('original')
			self.relax.data.mf_param_types.append(['S2'])
		elif model == 'm2':
			self.relax.data.mf_equation.append('original')
			self.relax.data.mf_param_types.append(['S2', 'te'])
		elif model == 'm3':
			self.relax.data.mf_equation.append('original')
			self.relax.data.mf_param_types.append(['S2', 'Rex'])
		elif model == 'm4':
			self.relax.data.mf_equation.append('original')
			self.relax.data.mf_param_types.append(['S2', 'te', 'Rex'])
		elif model == 'm5':
			self.relax.data.mf_equation.append('extended')
			self.relax.data.mf_param_types.append(['S2f', 'S2s', 'te'])
		else:
			print "The model '" + model + "' is invalid."
			print "[ failed ]"
			return

		self.relax.data.func = mf_functions(self.relax)

		# Create the mf_params data structure.
		for i in range(len(self.relax.data.seq)):
			self.relax.data.mf_params.append([None, None])

		print "[ OK ]"
