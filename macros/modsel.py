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
		self.set = x.set


class macro_class:
	def __init__(self, relax):
		"Class containing the macro for selecting which model selection method should be used."

		self.relax = relax


	def set(self, type=None):
		"Macro for selecting which model selection method should be used."

		if not type:
			print "No model selection method given."
			return

		self.relax.data.modsel = type
