
class set_model_selection:
	def __init__(self, relax):
		"Class containing the macro for selecting which model selection method should be used."

		self.relax = relax


	def set(self, type=None):
		"Macro for selecting which model selection method should be used."

		if not type:
			print "No model selection method given."
			return

		self.relax.data.modsel = type
